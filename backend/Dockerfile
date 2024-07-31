FROM nk-data-base
WORKDIR /app
COPY . .
COPY ./start.sh /start.sh
RUN chmod +x /start.sh
RUN pip install --no-cache-dir -r requirements.txt
EXPOSE 7666
CMD ["/start.sh"]