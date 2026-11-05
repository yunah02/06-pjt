# 06-pjt · ThRead 📚

> SSAFY 16기 관통 프로젝트 6회차 – **관계형 DB 설계**
> 도서를 등록하고, 읽은 뒤의 감상을 쓰레드(게시글)로 나누는 Django 도서 커뮤니티

| 항목 | 내용 |
| --- | --- |
| 프로젝트 / 앱 | `mypjt` / `accounts`, `books` |
| 사용 기술 | Python 3.11, Django 5.2, Bootstrap 5.3, SQLite, OpenAI API (gpt-5-nano), Wikipedia API |
| 팀원 | A: 최주희 (accounts) · B: 피윤아 (books) |
| 진행 상태 | 필수 기능 F601~F624 완료 · 심화 F625, F627, F628 완료 · CSS 적용 완료 |

---

## 목차

1. [실행 방법](#1-실행-방법)
2. [프로젝트 구조](#2-프로젝트-구조)
3. [ERD (모델 관계)](#3-erd-모델-관계)
4. [URL 구성](#4-url-구성)
5. [주요 기능](#5-주요-기능)
6. [요구사항 구현 현황](#6-요구사항-구현-현황)
7. [실행 결과 캡처](#7-실행-결과-캡처)
8. [협업 방식 (NF601)](#8-협업-방식-nf601)
9. [학습 내용](#9-학습-내용)
10. [느낀 점](#10-느낀-점)

---

## 1. 실행 방법

```bash
# 1. 가상환경 생성 및 활성화
python -m venv venv
source venv/Scripts/activate     # Windows (Git Bash)
# source venv/bin/activate       # macOS / Linux

# 2. 패키지 설치
pip install -r requirements.txt

# 3. 환경 변수 파일 만들기 (AI 작가 정보 기능에 필요)
cp .env.example .env
#    .env 파일을 열고 GMS_KEY, GMS_BASE_URL 값을 입력

# 4. DB 생성 (장르 카테고리 7개가 자동으로 들어감)
python manage.py migrate

# 5. 서버 실행
python manage.py runserver
```

- 메인 페이지: `http://127.0.0.1:8000/` → 도서 목록(`/books/`)으로 이동
- `.env`는 `settings.py`에서 `python-dotenv`로 읽습니다. `.env`가 없어도 서버는 실행됩니다. 이 경우 작가 정보만 "불러오지 못했습니다"로 표시됩니다.
- `.gitignore`로 `.env`, `db.sqlite3`, `media/`, `__pycache__/`, `venv/` 등은 제출하지 않습니다. API Key는 GitLab에 올라가지 않습니다.

---

## 2. 프로젝트 구조

```
06-pjt/
├── mypjt/                 # 프로젝트 설정 (settings.py, urls.py)
├── accounts/              # 회원 앱 (A 담당)
│   ├── models.py          # Category, User (AbstractUser 상속)
│   ├── forms.py           # CustomUserCreationForm, CustomUserChangeForm
│   ├── views.py           # login, logout, signup, profile, follow, people, update, delete, change_password
│   ├── migrations/0003_seed_categories.py   # 장르 7개 자동 생성 (RunPython)
│   └── templates/accounts/
├── books/                 # 도서 앱 (B 담당)
│   ├── models.py          # Book, Thread, Comment
│   ├── forms.py           # BookForm, ThreadForm, CommentForm
│   ├── views.py           # index, create, detail, update, delete, thread_*, like, comment_*
│   ├── ai.py              # 위키피디아 검색 + GPT 작가 정보 생성 (F625)
│   └── templates/books/   # _form.html (공용 폼 조각) 포함
├── templates/base.html    # 공통 레이아웃 + 반응형 Navbar
├── static/css/style.css   # 공통 스타일 (색상 변수, 카드, 버튼, 폼, 반응형)
├── .env.example           # 환경 변수 예시 (GMS_KEY, GMS_BASE_URL)
├── requirements.txt
└── .gitignore
```

---

## 3. ERD (모델 관계)

```mermaid
erDiagram
    USER ||--o{ BOOK : "작성 (1:N)"
    USER ||--o{ THREAD : "작성 (1:N)"
    USER ||--o{ COMMENT : "작성 (1:N)"
    BOOK ||--o{ THREAD : "도서의 쓰레드 (1:N)"
    THREAD ||--o{ COMMENT : "쓰레드의 댓글 (1:N)"
    CATEGORY |o--o{ BOOK : "도서 장르 (1:N)"
    USER }o--o{ THREAD : "좋아요 like_users (M:N)"
    USER }o--o{ USER : "팔로우 followings (M:N)"
    USER }o--o{ CATEGORY : "선호 장르 preferred_categories (M:N)"

    USER {
        string username
        string email
        string last_name
        string first_name
        string gender "M / F / O"
        int age
        int weekly_reading_time "주간 평균 독서 시간"
        int yearly_reading_count "연간 독서량"
        image profile_image
    }
    CATEGORY {
        string name "max 50"
    }
    BOOK {
        string title "max 100"
        text description
        float customer_review_rank "0 ~ 5"
        string author "max 50"
        int user_id FK
        int category_id FK "SET_NULL"
        text author_info "AI 생성"
        json author_works "AI 생성"
        url author_image "위키피디아"
    }
    THREAD {
        string title "max 100"
        text content
        date read_date
        datetime created_at "auto_now_add"
        datetime updated_at "auto_now"
        int book_id FK
        int user_id FK
    }
    COMMENT {
        string content "max 200"
        datetime created_at "auto_now_add"
        int thread_id FK
        int user_id FK
    }
```

| 관계 | 구현 코드 | 역참조 이름 |
| --- | --- | --- |
| User 1 : N Book | `Book.user = ForeignKey(AUTH_USER_MODEL)` | `user.book_set` |
| User 1 : N Thread | `Thread.user = ForeignKey(AUTH_USER_MODEL)` | `user.thread_set` |
| Book 1 : N Thread | `Thread.book = ForeignKey(Book)` | `book.thread_set` |
| Thread 1 : N Comment | `Comment.thread = ForeignKey(Thread)` | `thread.comment_set` |
| User 1 : N Comment | `Comment.user = ForeignKey(AUTH_USER_MODEL)` | `user.comment_set` |
| Category 1 : N Book | `Book.category = ForeignKey('accounts.Category', SET_NULL, null=True)` | `category.book_set` |
| User M : N Thread (좋아요) | `Thread.like_users = ManyToManyField(AUTH_USER_MODEL, related_name='like_threads')` | `user.like_threads` |
| User M : N User (팔로우) | `User.followings = ManyToManyField('self', symmetrical=False, related_name='followers')` | `user.followers` |
| User M : N Category (선호 장르) | `User.preferred_categories = ManyToManyField(Category, related_name='preferred_users')` | `category.preferred_users` |

- `Thread`는 `user`와 `like_users` 두 곳에서 User를 참조합니다. 그래서 역참조 이름이 겹치지 않도록 `like_users`에 `related_name='like_threads'`를 지정했습니다.
- `Book.category`는 `on_delete=SET_NULL`입니다. 카테고리가 삭제되어도 도서는 남고, 화면에는 "미분류"로 표시됩니다.
- 나머지 FK는 `on_delete=CASCADE`입니다. 도서가 삭제되면 쓰레드가, 쓰레드가 삭제되면 댓글이 함께 삭제됩니다.

---

## 4. URL 구성

URL은 모두 `app_name` + `name`으로 참조합니다 (`{% url 'books:detail' book.pk %}`). URL 문자열이 바뀌어도 템플릿과 view를 고칠 필요가 없습니다. (NF602)

### 메인

| URL | 동작 |
| --- | --- |
| `/` | `RedirectView`로 `books:index`에 redirect |

### books (`/books/`)

| URL | name | view | 허용 Method |
| --- | --- | --- | --- |
| `/books/` | `books:index` | index | GET |
| `/books/?category=<pk>` | `books:index` | index (카테고리 필터) | GET |
| `/books/create/` | `books:create` | create | GET, POST |
| `/books/<book_pk>/` | `books:detail` | detail | GET |
| `/books/<book_pk>/update/` | `books:update` | update | GET, POST |
| `/books/<book_pk>/delete/` | `books:delete` | delete | POST |
| `/books/<book_pk>/threads/create/` | `books:thread_create` | thread_create | GET, POST |
| `/books/threads/<thread_pk>/` | `books:thread_detail` | thread_detail | GET |
| `/books/threads/<thread_pk>/update/` | `books:thread_update` | thread_update | GET, POST |
| `/books/threads/<thread_pk>/delete/` | `books:thread_delete` | thread_delete | POST |
| `/books/threads/<thread_pk>/like/` | `books:like` | like | POST |
| `/books/threads/<thread_pk>/comments/` | `books:comment_create` | comment_create | POST |
| `/books/comments/<comment_pk>/delete/` | `books:comment_delete` | comment_delete | POST |

### accounts (`/accounts/`)

| URL | name | view | 허용 Method |
| --- | --- | --- | --- |
| `/accounts/login/` | `accounts:login` | login | GET, POST |
| `/accounts/logout/` | `accounts:logout` | logout | POST |
| `/accounts/signup/` | `accounts:signup` | signup | GET, POST |
| `/accounts/profile/<username>/` | `accounts:profile` | profile | GET |
| `/accounts/<user_pk>/follow/` | `accounts:follow` | follow | POST |
| `/accounts/people/` | `accounts:people` | people (추가 기능) | GET |
| `/accounts/update/` | `accounts:update` | update | GET, POST |
| `/accounts/delete/` | `accounts:delete` | delete | POST |
| `/accounts/password/` | `accounts:change_password` | change_password | GET, POST |

---

## 5. 주요 기능

### 5-1. 공통

- **Navbar** (`templates/base.html`): 모든 페이지가 `base.html`을 상속하므로 Navbar가 모든 페이지에 같게 출력됩니다.
  - 항상 보임: 로고(📖 ThRead), INDEX, PEOPLE
  - 로그인 전: LOGIN, SIGNUP
  - 로그인 후: CREATE, MY PROFILE, LOGOUT (POST form 버튼)
  - 화면이 좁으면 햄버거 버튼(`navbar-toggler`)으로 메뉴가 접힙니다.
- **메인 페이지**: `/`로 접속하면 도서 목록으로 이동합니다. 로그인, 로그아웃, 회원가입, 회원정보 수정, 비밀번호 변경, 회원탈퇴 후에도 모두 도서 목록으로 이동합니다.
- **HTTP Method 제한** (NF603): 모든 view에 `@require_safe`, `@require_POST`, `@require_http_methods(['GET', 'POST'])`를 붙였습니다. 허용하지 않은 Method로 요청하면 `405 Method Not Allowed`를 돌려줍니다.
- **로그인 필요 기능**: `@login_required`를 붙였습니다. 로그인하지 않은 사용자는 `/accounts/login/?next=...`로 이동합니다.
- **없는 데이터 처리**: profile, follow, like, comment view는 대상이 없으면 `Http404`를 발생시킵니다.
- **CSS** (`static/css/style.css`): Bootstrap 위에 공통 스타일을 덧씌웠습니다.
  - `:root`에 색상 변수를 모아 두고 전체에서 같은 색을 씁니다.
  - Navbar, 카드, 버튼, 리스트, 카테고리 필터(`nav-pills`), 배지, 폼, 프로필 사진 스타일
  - 태블릿(991px 이하), 모바일(576px 이하) 반응형 규칙

### 5-2. books 앱 (B)

**도서 (Book)**

- **목록 (index)**: 모든 도서를 최신순(`-pk`)으로 보여 줍니다. 제목, 저자, 평점을 출력하고, 항목을 누르면 상세 페이지로 이동합니다. 로그인한 경우에만 "도서 작성" 버튼이 보입니다.
- **카테고리 필터 (F628)**: 목록 위에 "전체"와 장르 7개 버튼이 있습니다. 버튼을 누르면 `?category=<pk>`로 요청하고, view에서 `filter(category_id=...)`로 걸러 냅니다. 선택한 버튼은 `active`로 표시됩니다. 숫자가 아닌 값은 무시하고 전체를 보여 줍니다.
- **작성 (create)**: `BookForm`으로 입력을 받습니다. `form.save(commit=False)`로 먼저 객체를 만들고, `book.user = request.user`로 작성자를 넣은 뒤 저장합니다. 그 다음 AI 작가 정보를 생성하고(F625), 상세 페이지로 redirect 합니다.
- **상세 (detail)**: 제목, 설명, 회원 리뷰 평점, 저자, 카테고리 배지, 작성자를 출력합니다. 그 아래에 작가 정보 카드, 쓰레드 목록(`book.thread_set`), "쓰레드 작성" 버튼을 보여 줍니다.
- **수정 (update)**: 기존 데이터를 `instance=book`으로 미리 채웁니다. 작성자가 아니면 수정하지 않고 상세 페이지로 돌려보냅니다.
- **삭제 (delete)**: POST 요청만 받습니다. 작성자만 삭제할 수 있고, 삭제 후 목록 페이지로 이동합니다.
- **평점 검증**: `customer_review_rank`는 `FloatField` + `MinValueValidator(0)`, `MaxValueValidator(5)`입니다. 0~5 밖의 값은 저장되지 않고 에러 메시지가 폼에 표시됩니다.

**AI 작가 정보 (F625, `books/ai.py`)**

도서를 저장한 직후 `fill_author_info(book)`가 실행됩니다.

1. **위키피디아 검색**: 한국어 위키피디아 API에 `"저자 이름 작가"`로 검색합니다. 결과 5개 중에서 제목에 저자 이름이 있고, 첫 150자에 "작가, 소설가, 시인..." 같은 단어가 있는 문서만 고릅니다. 동명이인이나 관계없는 문서를 거르기 위해서입니다. 문서 요약과 프로필 사진 URL을 가져옵니다.
2. **GPT 요청**: 도서 정보와 위키피디아 요약을 프롬프트에 넣고 `gpt-5-nano` 모델에 요청합니다. 프롬프트는 "모르면 지어내지 말 것", "JSON 형식으로만 답할 것"을 지시합니다.
3. **JSON 파싱**: 응답에서 `{`부터 `}`까지만 잘라 `json.loads`로 읽습니다.
4. **저장**: `author_info`(소개 글), `author_works`(대표작 최대 5개, JSONField), `author_image`(위키피디아 사진)를 `save(update_fields=[...])`로 저장합니다.
5. **실패 처리**: 네트워크 오류, API 오류, JSON 오류가 나도 예외를 밖으로 내보내지 않습니다. 도서는 정상으로 저장되고, 상세 페이지에 "작가 정보를 불러오지 못했습니다."가 표시됩니다.

- 상세 페이지 작가 정보 아래에 "작가 대표작과 작가 정보는 AI가 생성한 정보로, 정확하지 않을 수 있습니다." 안내 문구를 항상 출력합니다.
- API Key와 주소는 코드에 쓰지 않고 `.env`의 `GMS_KEY`, `GMS_BASE_URL`에서 읽습니다.

**쓰레드 (Thread)**

- **작성 (thread_create)**: URL의 `book_pk`로 도서를 찾고, `thread.book`과 `thread.user`를 view에서 넣은 뒤 저장합니다. 저장 후 쓰레드 상세 페이지로 이동합니다.
- **상세 (thread_detail)**: 제목, 본문, 독서일, 도서 제목, 작성자, 좋아요 수를 출력합니다. "도서로 돌아가기" 링크가 있습니다.
- **수정 (thread_update) / 삭제 (thread_delete)**: 작성자만 수정 링크와 삭제 버튼을 볼 수 있고, view에서도 작성자를 한 번 더 확인합니다. 삭제 후에는 그 쓰레드가 속한 도서의 상세 페이지로 이동합니다.
- **폼**: `ThreadForm`은 `title`, `content`, `read_date`만 입력받습니다. `book`, `user`는 사용자가 고칠 수 없게 view에서 넣습니다. 독서일은 `type="date"` 달력 입력입니다.
- **공용 폼 템플릿**: 도서/쓰레드의 작성·수정 페이지 4개가 `books/_form.html`을 `include`로 함께 씁니다. 필드마다 label, 입력칸, 에러 메시지를 출력합니다.

**좋아요 (F624)**

- 로그인한 사용자에게만 쓰레드 상세 페이지에 좋아요 버튼이 보입니다.
- 이미 좋아요를 눌렀으면 "좋아요 취소"(빨간 버튼), 아니면 "좋아요"(테두리 버튼)가 보입니다.
- view는 `like_users.filter(pk=...).exists()`로 확인한 뒤 `remove()` 또는 `add()`를 합니다. 처리 후 같은 쓰레드 상세 페이지로 redirect 합니다.
- POST만 받습니다. 로그인하지 않은 상태로 요청하면 로그인 페이지로 이동합니다.

**댓글 (F627)**

- 쓰레드 상세 페이지 아래에 댓글 수, 댓글 목록, 작성 폼이 있습니다.
- 댓글 옆에 작성자 이름이 있고, 누르면 그 사람의 프로필 페이지로 이동합니다.
- 로그인한 사용자만 댓글 입력칸이 보입니다. 로그인하지 않으면 "로그인 후 댓글을 작성할 수 있습니다."가 보입니다.
- `CommentForm`으로 검증하고, `thread`와 `user`는 view에서 넣습니다. 댓글은 최대 200자입니다.
- 본인 댓글에만 삭제 버튼이 보이고, view에서도 작성자를 확인합니다.

### 5-3. accounts 앱 (A)

- **User 모델**: `AbstractUser`를 상속하고 성별, 나이, 주간 평균 독서 시간, 연간 독서량, 프로필 사진(`ImageField`), 팔로우(`followings`), 선호 카테고리(`preferred_categories`)를 추가했습니다. `settings.AUTH_USER_MODEL = 'accounts.User'`
- **회원가입 (signup)**: `UserCreationForm`을 상속한 `CustomUserCreationForm`을 씁니다. 프로필 사진 업로드를 위해 `request.FILES`와 `enctype="multipart/form-data"`를 사용합니다. 선호 카테고리는 체크박스(`CheckboxSelectMultiple`)로 여러 개 고를 수 있습니다. 가입 후 바로 로그인하고 메인으로 이동합니다.
- **로그인 / 로그아웃**: `AuthenticationForm`, `auth_login`, `auth_logout`을 사용합니다. 로그아웃은 POST만 받습니다. 이미 로그인한 사용자가 로그인·회원가입 페이지에 오면 메인으로 돌려보냅니다.
- **프로필 (profile)**: 누구나 볼 수 있습니다. 회원 정보, 팔로워 수, 팔로잉 수, 선호 카테고리, 작성한 쓰레드 목록(쓰레드 제목 + 도서 제목)을 보여 줍니다. 내 프로필이면 "회원정보 수정 / 회원탈퇴", 다른 사람 프로필이면 "팔로우 / 언팔로우" 버튼이 보입니다.
- **팔로우 (follow)**: POST만 받습니다. 이미 팔로우했으면 취소하고, 아니면 팔로우합니다. 자기 자신은 팔로우할 수 없습니다. 처리 후 그 사람의 프로필로 돌아갑니다.
- **회원정보 수정 (update)**: `UserChangeForm`을 상속하고 `password = None`으로 비밀번호 안내 영역을 감췄습니다. `is_staff` 같은 관리용 필드는 출력하지 않습니다. 선호 카테고리도 여기서 바꿀 수 있습니다.
- **비밀번호 변경 (change_password)**: `PasswordChangeForm`을 사용합니다. 변경 후 `update_session_auth_hash`로 세션을 갱신하여 로그아웃되지 않습니다. 회원정보 수정 페이지에 링크가 있습니다.
- **회원탈퇴 (delete)**: POST만 받습니다. 확인 창(`confirm`)을 띄운 뒤 탈퇴하고 로그아웃 처리합니다.
- **카테고리 (F628)**: `Category` 모델을 만들고, `0003_seed_categories.py` 데이터 migration으로 장르 7개(소설/시/희곡, 경제/경영, 자기계발, 인문/교양, 취미/실용, 어린이/청소년, 과학)를 자동으로 넣었습니다. `migrate`만 하면 바로 쓸 수 있습니다.
- **추가 기능 – PEOPLE 페이지**: 전체 사용자를 팔로워 수 순서로 보여 줍니다 (`annotate(Count('followers', distinct=True))`). 로그인한 경우, 아직 팔로우하지 않은 사용자 중 **나와 선호 장르가 많이 겹치는 사람** 5명을 "추천 친구"로 보여 줍니다. 겹치는 장르 수는 배지로 표시합니다.

---

## 6. 요구사항 구현 현황

> ✅ 완료 · ➖ 구현하지 않음

### 필수

| 번호 | 요구사항 | 담당 | 상태 | 비고 |
| --- | --- | --- | --- | --- |
| F601 | 프로젝트 구성 | 공통 | ✅ | `mypjt`, `accounts`, `books` |
| F602 | User Model | A | ✅ | |
| F603 | User Form | A | ✅ | |
| F604 | Book Model | B | ✅ | |
| F605 | Thread Model | B | ✅ | `like_users` M:N 포함 |
| F606 | Book / Thread Form | B | ✅ | ModelForm |
| F607 | login | A | ✅ | |
| F608 | logout | A | ✅ | |
| F609 | signup | A | ✅ | |
| F610 | profile | A | ✅ | 작성한 쓰레드 목록 포함 |
| F611 | follow | A | ✅ | |
| F612 | update | A | ✅ | |
| F613 | delete | A | ✅ | |
| F614 | change_password | A | ✅ | |
| F615 | index | B | ✅ | |
| F616 | create | B | ✅ | |
| F617 | detail | B | ✅ | |
| F618 | update | B | ✅ | |
| F619 | delete | B | ✅ | |
| F620 | thread_create | B | ✅ | |
| F621 | thread_detail | B | ✅ | 좋아요 버튼 포함 |
| F622 | thread_update | B | ✅ | |
| F623 | thread_delete | B | ✅ | |
| F624 | like | A | ✅ | |
| NF601 | Git 활용 | 공통 | ✅ | [8장](#8-협업-방식-nf601) 참고 |
| NF602 | URL 구성 | 공통 | ✅ | `app_name` + URL name |
| NF603 | HTTP Method 허용 | 공통 | ✅ | 데코레이터로 제한 |
| - | CSS 프론트엔드 | 공통 | ✅ | Bootstrap + `style.css` |

### 심화

| 번호 | 요구사항 | 담당 | 상태 | 비고 |
| --- | --- | --- | --- | --- |
| F625 | AI 작가 정보 생성 및 저장 | 최주희 | ✅ | 위키피디아 + `gpt-5-nano` |
| F626 | AI 쓰레드 커버 이미지 | - | ➖ | 구현하지 않음 |
| F627 | 쓰레드 댓글 | 최주희 | ✅ | Comment 모델, 작성·삭제 |
| F628 | 카테고리 | 최주희 | ✅ | 선호 장르(M:N), 도서 장르(1:N), 목록 필터 |

### 알려진 한계 / 개선할 점

- [ ] `BookForm`이 `exclude = ('user',)`라서 AI가 채우는 `author_info`, `author_works`, `author_image` 입력칸도 도서 작성·수정 화면에 보입니다. `exclude`에 세 필드를 추가하면 숨길 수 있습니다.
- [ ] AI 작가 정보는 도서를 **처음 작성할 때만** 생성됩니다. 수정에서 저자 이름을 바꾸면 작가 정보가 다시 생성되지 않습니다.
- [ ] AI 요청은 도서 저장 요청 안에서 바로 실행됩니다. 응답이 느리면 작성 버튼을 누른 뒤 페이지 이동까지 시간이 걸립니다. (timeout 60초)
- [ ] `accounts/admin.py`, `books/admin.py`에 모델이 등록되어 있지 않습니다.
- [ ] books view는 팀 규칙대로 `Model.objects.get(pk=...)`를 씁니다. 없는 도서·쓰레드 번호로 접근하면 404가 아니라 500 에러가 납니다.

---

## 7. 실행 결과 캡처

> 이미지는 `images/` 폴더에 넣고 아래 경로를 맞춰 주세요.

### 공통
| 화면 | 캡처 |
| --- | --- |
| Navbar – 로그인 전 | ![navbar-logout](images/navbar_before_login.png) |
| Navbar – 로그인 후 | ![navbar-login](images/navbar_after_login.png) |
| Navbar – 모바일 (메뉴 접힘) | ![navbar-mobile](images/navbar_mobile.png) |

### accounts
| 번호 | 화면 | 캡처 |
| --- | --- | --- |
| F607 | 로그인 | ![F607](images/F607_login.png) |
| F608 | 로그아웃 후 화면 | ![F608](images/F608_logout.png) |
| F609 | 회원가입 (선호 카테고리 체크박스) | ![F609](images/F609_signup.png) |
| F610 | 프로필 (내 프로필 / 다른 사람 프로필) | ![F610](images/F610_profile.png) |
| F611 | 팔로우 / 언팔로우 | ![F611](images/F611_follow.png) |
| F612 | 회원정보 수정 | ![F612](images/F612_update.png) |
| F613 | 회원탈퇴 | ![F613](images/F613_delete.png) |
| F614 | 비밀번호 변경 | ![F614](images/F614_change_password.png) |
| 추가 | PEOPLE (추천 친구) | ![people](images/people.png) |

### books
| 번호 | 화면 | 캡처 |
| --- | --- | --- |
| F615 | 도서 목록 | ![F615](images/F615_index.png) |
| F616 | 도서 작성 | ![F616](images/F616_create.png) |
| F616 | 도서 작성 – 평점 6 입력 시 에러 메시지 | ![F616-error](images/F616_create_error.png) |
| F617 | 도서 상세 (작성자 / 다른 사용자) | ![F617](images/F617_detail.png) |
| F618 | 도서 수정 (기존 값 채워짐) | ![F618](images/F618_update.png) |
| F619 | 도서 삭제 후 목록 | ![F619](images/F619_delete.png) |
| F620 | 쓰레드 작성 | ![F620](images/F620_thread_create.png) |
| F621 | 쓰레드 상세 | ![F621](images/F621_thread_detail.png) |
| F622 | 쓰레드 수정 | ![F622](images/F622_thread_update.png) |
| F623 | 쓰레드 삭제 후 도서 상세 | ![F623](images/F623_thread_delete.png) |
| F624 | 좋아요 / 좋아요 취소 | ![F624](images/F624_like.png) |
| NF603 | GET으로 삭제 URL 접근 시 405 | ![NF603](images/NF603_405.png) |

---

## 8. 협업 방식 (NF601)

### 8-1. 역할 분담

| 담당 | 앱 | 요구사항 |
| --- | --- | --- |
| A (최주희) | accounts | F601~F603, F607~F614, F624 (like) |
| B (피윤아) | books | F604~F606, F615~F623 |
| 최주희 | 심화 | F625, F627, F628 |

- 작업 전에 **필드명과 URL name을 먼저 합의**했습니다. 그래서 상대의 코드가 아직 없어도 각자 작업할 수 있었습니다.
  - Book: `title`, `description`, `customer_review_rank`, `author`, `user`
  - Thread: `title`, `content`, `read_date`, `created_at`, `updated_at`, `book`, `user`, `like_users (related_name='like_threads')`
  - 메인 페이지: `books:index`
- 코드 스타일도 맞췄습니다. view에서 객체를 조회할 때 두 사람 모두 `Model.objects.get(pk=...)`를 사용합니다.

### 8-2. Branch 원칙

GitHub Flow를 참고하여 단순하게 운영했습니다.

| Branch | 용도 | 사용 방법 |
| --- | --- | --- |
| `master` | 제출용 기본 브랜치. 항상 실행되는 코드만 둠 | 직접 commit하지 않음. Merge Request(MR)로만 합침 |
| `book` | B의 books 앱 작업 | `master`에서 분기 → 작업·commit → push → MR → `master`에 merge |
| `A 브랜치 이름 입력` | A의 accounts 앱 작업 | `master`에서 분기 → 작업·commit → push → MR → `master`에 merge |

**작업 흐름**

```bash
# 1. 최신 master 받기
git switch master
git pull origin master

# 2. 내 브랜치로 이동 (처음이면 -c 로 생성)
git switch book            # 또는: git switch -c book

# 3. 최신 master 내용을 내 브랜치에 반영
git merge master

# 4. 작업 후 commit
git add .
git commit -m "feat: 도서 상세 페이지 구현"

# 5. push 후 GitLab에서 Merge Request 생성
git push -u origin book
```

**Merge 순서 합의**

공유 파일(`base.html`, `urls.py`)이 있어서 순서를 정했습니다.

1. A: 프로젝트 뼈대 + accounts → `master`
2. B: books → `master`
3. A: profile 쓰레드 목록 + like → `master`
4. B: 좋아요 버튼 연결 → `master`

### 8-3. Commit 메시지 원칙

**형식**: `타입: 무엇을 했는지 (한국어, 한 줄)`

| 타입 | 의미 | 예시 |
| --- | --- | --- |
| `feat` | 새 기능 | `feat: Thread 모델 생성` |
| `fix` | 버그 수정 | `fix: 쓰레드 삭제 후 redirect 경로 수정` |
| `style` | CSS, 화면 꾸미기 (기능 변화 없음) | `style: navbar 색상 변경` |
| `refactor` | 동작은 같고 코드 구조만 바꿈 | `refactor: 작성/수정 폼을 _form.html로 분리` |
| `docs` | README 등 문서 | `docs: README 협업 원칙 작성` |
| `chore` | 설정, 패키지, .gitignore | `chore: requirements.txt 추가` |

**Commit 시점**

- 기능 1개가 **실제로 동작하는 것을 확인한 뒤** commit 합니다. (예: model + migration 1번, view + template 1번)
- 서버가 실행되지 않는 상태로는 commit 하지 않습니다.
- push 전에 `git status`로 `db.sqlite3`, `__pycache__`, `venv`가 포함되지 않았는지 확인합니다.

### 8-4. 문제 상황과 원인 분석

**① `base.html` merge conflict**

- **상황**: `book` → `master` MR에서 `templates/base.html`에 conflict가 발생했습니다.
- **원인**: A와 B가 같은 파일의 **같은 줄(Navbar 링크)**을 각자 수정했습니다. A는 accounts 링크를 넣었고, B는 INDEX, CREATE, 로고 링크를 `books:index`, `books:create`로 바꿨습니다. Git은 두 변경 중 어느 것을 남길지 스스로 정할 수 없습니다.
- **해결**: B가 conflict 부분을 직접 확인했습니다. 두 사람의 링크를 모두 남기도록 합친 뒤 commit 하고 merge 했습니다.
- **배운 점**: 여러 사람이 고치는 공유 파일(`base.html`, `mypjt/urls.py`, `settings.py`)은 **한 사람이 담당**하거나, 수정 전에 서로 알리는 것이 좋습니다.

**② 상대 코드가 없을 때 `NoReverseMatch` 에러**

- **상황**: books만 있을 때 모든 페이지에서 `NoReverseMatch` 에러가 났습니다.
- **원인**: `base.html`이 `accounts:login` 같은 URL name을 쓰는데, 그때는 `accounts/urls.py`가 비어 있었습니다.
- **해결**: 로컬에서만 임시 accounts URL을 만들어 테스트했고, 그 파일은 commit 하지 않았습니다. A의 accounts가 merge된 뒤 정상 동작을 확인했습니다.
- **배운 점**: URL name을 미리 합의해도, 실제 코드가 들어오는 **merge 순서**가 중요합니다.

### 8-5. 원칙 점검 (프로젝트 종료 시)

| 원칙 | 지켜졌는가 | 근거 / 반성 |
| --- | --- | --- |
| `master`에 직접 commit 하지 않기 | ⬜ 확인 필요 | 초기 프로젝트 뼈대 commit 확인 필요 |
| 기능별 브랜치에서 작업 후 MR로 merge | ✅ | `book` → `master` MR로 merge |
| merge 전 `master` 최신 내용 반영 | ⬜ 확인 필요 | `base.html` conflict는 MR 단계에서 발견됨 |
| commit 메시지 `타입: 내용` 형식 | ⬜ 확인 필요 | GitLab commit 목록 기준으로 점검 |
| 동작 확인 후 commit | ⬜ 확인 필요 | |
| 불필요한 파일 제출하지 않기 | ✅ | `.gitignore` 적용 (`db.sqlite3`, `media/`, `__pycache__/`) |
| 합의한 필드명 / URL name 지키기 | ✅ | 두 앱 코드가 수정 없이 연결됨 |

---

## 9. 학습 내용

### 9-1. N:1 관계 (ForeignKey)

- `Thread.book = ForeignKey(Book, on_delete=CASCADE)`로 "쓰레드 N개 : 도서 1개"를 만듭니다.
- DB에는 `book_id` 컬럼이 생깁니다.
- 정참조: `thread.book.title` / 역참조: `book.thread_set.all()`
- 작성자, 도서처럼 **사용자가 입력하면 안 되는 FK**는 폼에서 빼고 view에서 넣습니다.

```python
thread = form.save(commit=False)   # DB 저장 전 객체만 생성
thread.book = book                 # URL로 받은 도서
thread.user = request.user         # 로그인한 사용자
thread.save()
```

### 9-2. M:N 관계 (ManyToManyField)

- 좋아요와 팔로우는 "여러 사용자 : 여러 대상" 관계입니다. Django가 **중간 테이블**을 자동으로 만듭니다.
- 한 모델이 User를 두 번 참조하면 역참조 이름이 충돌합니다. 그래서 `related_name`으로 이름을 바꿉니다.
  - `user.thread_set` → 내가 **쓴** 쓰레드
  - `user.like_threads` → 내가 **좋아요한** 쓰레드
- 자기 자신과 M:N인 팔로우는 `symmetrical=False`가 필요합니다. 그래야 "내가 팔로우 = 상대도 나를 팔로우"가 되지 않습니다.
- `add()`, `remove()`, `filter(...).exists()`로 토글 기능을 만듭니다.

### 9-3. ModelForm과 유효성 검증

- `exclude` / `fields`로 사용자에게 보여 줄 필드를 정합니다.
- 모델의 `validators`(평점 0~5)가 `form.is_valid()`에서 자동으로 검사됩니다.
- `instance=`를 넘기면 수정 폼에 기존 값이 채워지고, `save()`가 UPDATE로 동작합니다.
- 작성 / 수정 화면이 같은 폼이라서 `_form.html`로 분리하고 `include`로 재사용했습니다.

### 9-4. Django 인증 시스템

- `AbstractUser`를 상속하면 기본 인증 기능은 그대로 쓰고 필드만 추가할 수 있습니다. `AUTH_USER_MODEL`은 **첫 migrate 전에** 설정해야 합니다.
- 다른 앱에서 User를 참조할 때는 `settings.AUTH_USER_MODEL`, view에서는 `get_user_model()`을 씁니다.
- 비밀번호 변경 후에는 세션 해시가 바뀌므로 `update_session_auth_hash`가 필요합니다.

### 9-5. 권한과 HTTP Method

- 템플릿에서 버튼을 숨기는 것만으로는 부족합니다. URL을 직접 입력할 수 있으므로 **view에서도 작성자를 확인**해야 합니다.
- 데이터를 바꾸는 요청(삭제, 로그아웃, 팔로우, 좋아요)은 `@require_POST` + CSRF 토큰으로 보호합니다.
- 데코레이터 순서: `@login_required`를 위에 둡니다. 로그인 확인을 먼저 합니다.

### 9-6. 데이터 migration과 카테고리

- 카테고리처럼 **처음부터 있어야 하는 데이터**는 `RunPython` 데이터 migration으로 넣을 수 있습니다. 팀원 모두 `migrate`만 하면 같은 장르 7개를 갖게 됩니다.
- `get_or_create`를 쓰면 migration을 여러 번 실행해도 중복이 생기지 않습니다. 되돌리기 함수(`remove_categories`)도 함께 작성했습니다.
- 다른 앱의 모델은 `'accounts.Category'`처럼 문자열로 참조할 수 있습니다.
- GET 파라미터(`?category=1`)로 필터를 만들 때는 값이 숫자인지 먼저 확인해야 합니다 (`isdigit()`).
- `annotate(Count(..., filter=Q(...), distinct=True))`로 "겹치는 선호 장르 수"처럼 조건이 있는 개수를 DB에서 바로 셀 수 있습니다.

### 9-7. 외부 API와 생성형 AI 연동

- API Key는 코드에 쓰지 않고 `.env` + `python-dotenv`로 읽습니다. `.env`는 `.gitignore`에 넣고, 팀원에게는 `.env.example`로 형식만 공유합니다.
- AI 응답은 항상 원하는 형식으로 오지 않습니다. 프롬프트로 JSON 형식을 지시하고, 코드에서도 `{ }` 부분만 잘라 파싱하고 타입을 확인합니다.
- 외부 API가 실패해도 서비스의 핵심 기능(도서 저장)은 멈추면 안 됩니다. 그래서 AI 부분을 `try/except`로 감싸고, 실패하면 안내 문구만 보여 줍니다.
- 위키피디아 검색 결과를 그대로 믿지 않고, 제목과 첫 문장을 검사해서 **엉뚱한 문서를 거르는 단계**를 두었습니다. AI가 사실이 아닌 내용을 만드는 것을 줄이기 위해서입니다.

### 9-8. Git 협업

- 브랜치를 나누면 동시에 작업할 수 있지만, **공유 파일**에서는 conflict가 생깁니다.
- conflict는 에러가 아니고, Git이 사람에게 선택을 요청하는 것입니다. `<<<<<<<`, `=======`, `>>>>>>>` 사이를 읽고 남길 코드를 정합니다.

---

## 10. 느낀 점

**A (최주희 · accounts)**

- 회원 기능을 맡으면서 Django가 이미 많은 것을 만들어 두었다는 것을 느꼈다. AbstractUser와 기본 Form을 상속하니, 나는 필요한 필드와 화면에만 집중할 수 있었다.
- 비밀번호를 바꾸면 로그아웃되고, 프로필 사진이 저장되지 않는 문제를 하나씩 찾아가는 과정이 가장 기억에 남는다. 덕분에 세션과 파일 업로드의 동작을 이해했다.
- 팔로우를 만들며 User가 User를 참조하는 관계가 신기했다. PEOPLE 페이지와 추천 친구까지 만들면서, 배운 ORM을 내 아이디어에 써 보는 재미를 느꼈다.
- books 코드가 없을 때 연결 부분을 TODO로 남기고 기다렸다. 협업에서는 내 코드가 팀원 코드와 어디서 만나는지 계속 생각해야 한다는 것을 배웠다.

**B (피윤아 · books)**

- 비슷한 CRUD 기능을 9개 반복해 만드니, 처음엔 헷갈리던 흐름(GET이면 화면, POST면 저장)이 자연스럽게 손에 익었다.
- 작성자 확인 코드를 쓰면서 "버튼을 숨기는 것"과 "실제로 막는 것"은 다르다는 것을 깨달았다.
- 작성·수정 화면을 _form.html 하나로 합치면서, 중복을 줄이면 나중에 고칠 때 편하다는 것을 직접 느꼈다.
- base.html conflict를 처음 직접 해결했다. 둘이 같은 줄을 고친 것이 원인이었고, 코드 실력만큼 미리 정하고 소통하는 것이 중요하다는 것을 배웠다.
- 필드명과 URL 이름을 먼저 맞춘 덕분에, 상대 코드 없이도 내 부분을 끝까지 만들 수 있었다. 다음 프로젝트에서도 이 방식을 쓰고 싶다.
