FROM python:3.12-slim
WORKDIR /app
COPY zone/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY zone .
RUN chmod a+x start.sh
ADD data/ /data
ADD shared/nk_shared nk_shared
CMD ["sh", "start.sh"]
