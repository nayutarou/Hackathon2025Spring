from pathlib import Path
import os
import environ

# 環境変数を管理するためのenvオブジェクト作成
env = environ.Env()
# .envファイルの読み込み
env.read_env('.env')
# .envファイルからSECRET_KEYを読み込み
SECRET_KEY = env('SECRET_KEY')
# .envファイルからDEBUGの値を取得し、真偽値に変換
DEBUG = env.bool('DEBUG', default=False)
# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

DEBUG=True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_extensions',
    'attendances.apps.AttendancesConfig',
    'subjects.apps.SubjectsConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        # Djangoに「テンプレートファイルを検索する追加のディレクトリ」を教えるための設定。
        'DIRS': [BASE_DIR / 'templates'], # テンプレート用のフォルダを追記
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': env('DATABASE_ENGINE', default='django.db.backends.sqlite3'),
        'NAME': env('DATABASE_DB', default=os.path.join(BASE_DIR, 'db.sqlite3')),
        # 以下は、MySQLやPostgreSQLの場合に設定
        # 'USER': env('DATABASE_USER', default='django_user'),
        # 'PASSWORD': env('DATABASE_PASSWORD', default='password'),
        # 'HOST': env('DATABASE_HOST', default='localhost'),
        # 'PORT': env('DATABASE_PORT', default='5432'),
    }
}

# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = 'static/'
# Djangoに「静的ファイルを検索する追加のディレクトリ」を教えるための設定。
STATICFILES_DIRS = [BASE_DIR / 'static'] # 静的ファイルのディレクトリの場所

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

ALLOWED_HOSTS = ['localhost', '127.0.0.1']