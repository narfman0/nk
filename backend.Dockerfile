FROM python:3.12-slim
WORKDIR /app
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY backend .
RUN chmod a+x start.sh
ADD data/ /data
ADD shared/nk_shared nk_shared
ENV PORT=7666
EXPOSE 7666
CMD ["sh", "start.sh"]