"""
Django settings for buzzword project.

Generated by 'django-admin startproject' using Django 2.2.7.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.2/ref/settings/
"""
import os
import tempfile

X_FRAME_OPTIONS = "SAMEORIGIN"

DATA_UPLOAD_MAX_MEMORY_SIZE = 200000000

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "_^vo*lm=7o!zoj4c6zi*di!kw5ovar@*@%subhxmv*pu=)!-w5"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ["127.0.0.1", "0.0.0.0", "localhost", "127.0.0.1:8000", "172.23.3.66"]

# APPEND_SLASH = False

# Application definition

INSTALLED_APPS = [
    "dpd_static_support",
    "start.apps.StartConfig",
    "example.apps.ExampleConfig",
    "explore.apps.ExploreConfig",
    "compare.apps.CompareConfig",
    "django_plotly_dash.apps.DjangoPlotlyDashConfig",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "guardian",
    "accounts",
    "martor",
    "markdownify",
    "bootstrap_modal_forms",
    "widget_tweaks"
]

STATICFILES_FINDERS = [
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
    "django_plotly_dash.finders.DashAssetFinder",
    "django_plotly_dash.finders.DashComponentFinder",
    "django_plotly_dash.finders.DashAppDirectoryFinder",
]


PLOTLY_COMPONENTS = [
    # Common components
    "dash_core_components",
    "dash_html_components",
    "dash_renderer",
    "dash_daq",
    "dash_table",
    # django-plotly-dash components
    "dpd_components",
    # static support if serving local assets
    "dpd_static_support",
    # Other components, as needed
    "dash_bootstrap_components",
]

# STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MIDDLEWARE = [
    "django_plotly_dash.middleware.ExternalRedirectionMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django_plotly_dash.middleware.BaseMiddleware",
]


PLOTLY_DASH = {
    "serve_locally": False,
}


ROOT_URLCONF = "buzzword.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, "buzzword", "templates")],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "accounts.context_processors.forms",
            ],
        },
    },
]

WSGI_APPLICATION = "buzzword.wsgi.application"

# from https://github.com/agusmakmun/django-markdown-editor
MARTOR_ENABLE_CONFIGS = {
    "emoji": False,  # to enable/disable emoji icons.
    "imgur": False,  # to enable/disable imgur/custom uploader.
    "mention": False,  # to enable/disable mention
    "jquery": False,  # to include/revoke jquery (require for admin default django)
    "living": False,  # to enable/disable live updates in preview
    "spellcheck": False,  # to enable/disable spellcheck in form textareas
    "hljs": False,  # to enable/disable hljs highlighting in preview
}
# don't know why it wants bools as strings...
MARTOR_ENABLE_CONFIGS = {k: str(v).lower() for k, v in MARTOR_ENABLE_CONFIGS.items()}

MARTOR_MARKDOWN_EXTENSIONS = [
    "markdown.extensions.extra",
    "markdown.extensions.nl2br",
    # 'markdown.extensions.smarty',
    # 'markdown.extensions.fenced_code',
    #  Custom markdown extensions.
    # 'martor.extensions.urlize',
    # 'martor.extensions.del_ins',    # ~~strikethrough~~ and ++underscores++
    # 'martor.extensions.mention',    # to parse markdown mention
    # 'martor.extensions.emoji',      # to parse markdown emoji
    # 'martor.extensions.mdx_video',  # to parse embed/iframe video
]

# CSRF_COOKIE_HTTPONLY = False

# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": os.path.join(BASE_DIR, "db.sqlite3"),
    }
}


# Password validation
# https://docs.djangoproject.com/en/2.2/ref/settings/#auth-password-validators
vali = "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": vali},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

AUTHENTICATION_BACKENDS = (
    "django.contrib.auth.backends.ModelBackend",
    "guardian.backends.ObjectPermissionBackend",
)

# Internationalization
# https://docs.djangoproject.com/en/2.2/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.2/howto/static-files/

PLOTLY_DASH = {
    # Route used for the message pipe websocket connection
    "ws_route": "dpd/ws/channel",
    # Route used for direct http insertion of pipe messages
    "http_route": "dpd/views",
    # Flag controlling existince of http poke endpoint
    "http_poke_enabled": True,
    # Insert data for the demo when migrating
    "insert_demo_migrations": False,
    # Timeout for caching of initial arguments in seconds
    "cache_timeout_initial_arguments": 60,
    # Name of view wrapping function
    "view_decorator": None,
    # Flag to control location of initial argument storage
    "cache_arguments": True,
    # Flag controlling local serving of assets
    "serve_locally": False,
}


STATIC_URL = "/static/"
STATICFILES_DIRS = ["static"]
MEDIA_URL = "/media/"
STATIC_ROOT = os.path.join(tempfile.gettempdir(), "buzzword_static")
MEDIA_ROOT = os.path.join(tempfile.gettempdir(), "buzzword_media")


# if true, do <meta page=n/>
# if false, leave as is
# if None, remove them
COMPARE_HANDLE_PAGE_NUMBERS = True

MARKDOWNIFY_MARKDOWN_EXTENSIONS = ['markdown.extensions.fenced_code',
                                   'markdown.extensions.extra']

MARKDOWNIFY_WHITELIST_STYLES = [
    'color',
    'font-weight',
    'font-size',
]

MARKDOWNIFY_WHITELIST_TAGS = [
  'a',
  'h1',
  'h2',
  'h3',
  'abbr',
  'acronym',
  'div',
  'img',
  'b',
  'blockquote',
  'em',
  'i',
  'li',
  'ol',
  'p',
  'span',
  'strong',
  'ul'
]

MARKDOWNIFY_WHITELIST_ATTRS = [
    'href',
    'src',
    'class',
    'alt',
    'width',
    'height',
    'display'
]

# BUZZWORD from env
CORPORA_FILE = "corpora.json"
LOAD_CORPORA = True
LOAD_LAYOUTS = True
# explorer settings 
DROP_COLUMNS = {"text", "parse"}
PAGE_SIZE = 25
TABLE_SIZE = (5000, 200)
ADD_GOVERNOR = False
MAX_CONC = 999
MAX_DATASET_ROWS = None

# path to tessdata -- needed to find the models
# make sure tessdata is always in repo root
PWD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TESSDATA_PREFIX = os.path.join(PWD, "tessdata")

# this should be set to none, or a corpus slug
BUZZWORD_SPECIFIC_CORPUS = "swiss-law"
