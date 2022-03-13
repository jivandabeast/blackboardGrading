#!/bin/bash

read -p "What is the assignment? " assignment

cd gradeFiles
cd $assignment
cd file_submissions

mkdir file
mv * file/

mkdir txt
mv file/*.txt txt/