#  `gettext` Notes

```shell
mkdir -p assets/locales/{en,fr}/LC_MESSAGES
pygettext3 -p assets/locales/ streamlit_app.py
cp assets/locales/messages.pot assets/locales/en/LC_MESSAGES/messages.po
cp assets/locales/messages.pot assets/locales/fr/LC_MESSAGES/messages.po
msgfmt -o assets/locales/en/LC_MESSAGES/messages.mo assets/locales/en/LC_MESSAGES/messages.po
msgfmt -o assets/locales/fr/LC_MESSAGES/messages.mo assets/locales/fr/LC_MESSAGES/messages.po
```
