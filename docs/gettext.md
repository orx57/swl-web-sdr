#  `gettext` Notes

```shell
mkdir -p locales/{en,fr}/LC_MESSAGES
pygettext3 -p locales streamlit_app.py
cp locales/messages.pot locales/en/LC_MESSAGES/messages.po
cp locales/messages.pot locales/fr/LC_MESSAGES/messages.po
msgfmt -o locales/en/LC_MESSAGES/messages.mo locales/en/LC_MESSAGES/messages.po
msgfmt -o locales/fr/LC_MESSAGES/messages.mo locales/fr/LC_MESSAGES/messages.po
```
