FROM python:3.5-onbuild
COPY webapp/ /usr/src/app
CMD ["python", "-O", "run.py"]
EXPOSE 8088
