#!/bin/sh

echo "# Generated using generate-pro.sh" > series60-remote.pro
echo "# " >> series60-remote.pro
echo "# Created: " `date -R` >> series60-remote.pro
echo "# WARNING! All changes made in this file will be lost!" >> series60-remote.pro
echo "" >> series60-remote.pro

FILES=$(find devices/ lib/ widget/ window/ -name "*.py")
for file in $FILES
do
   echo "SOURCES      +=  $file" >> series60-remote.pro
done

FILES=$(find ui/ -name "*.ui")
for file in $FILES
do
   echo "FORMS        +=  $file" >> series60-remote.pro
done

FILES=$(find ui/ -name "*.rc")
for file in $FILES
do
   echo "RESOURCES    +=  $file" >> series60-remote.pro
done

FILES=$(find lang/ -name "app_*.ts")
for file in $FILES
do
   echo "TRANSLATIONS +=  $file" >> series60-remote.pro
done
