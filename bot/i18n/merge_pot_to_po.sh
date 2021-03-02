#!/bin/bash
for file in ./bot/i18n/*/LC_MESSAGES/*.po; do msgmerge --update ${file} ./bot/i18n/base.pot; done
rm ./bot/i18n/*/LC_MESSAGES/*.po~
