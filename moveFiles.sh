#!/bin/bash

mkdir gradeFiles/$1/file_submissions/file
mv gradeFiles/$1/file_submissions/* gradeFiles/$1/file_submissions/file/

mkdir gradeFiles/$1/file_submissions/txt
mv gradeFiles/$1/file_submissions/file/*.txt gradeFiles/$1/file_submissions/txt/