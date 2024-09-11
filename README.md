<h1>Проект web_store (EthB2B).</h1>
Проект IaC в облаке Yandex Cloud. 
Terraform создает ВМ, балансировщики и S3, а Ansible устанавливает и настраивает приложения.
Сам проект представляет real-time аукцион вещей, созданный на микросервисной архитектуре, работающей по WebSocket с клиентом.
Пользователи указывают свои криптокошельки и предлагают свою цену за товар, причем данная сумма должна присутствовать.
Приложение находится в Kubernetes кластере, Jenkins осуществляет CI/CD приложения, обновления приложения происходят через Helm стратегией rolling update для Deployments.
Prometheus собирает метрики от Node_exporter и kube_state_metrics для визуализации в Grafana.
Для отправки сообщений в архитектуре имеется RabbitMQ и микросервис забирающий из него сообщения и отправляющий рассылку о новых лотах через Telegram бота.

**Технологии:** Terraform, Ansible, Prometheus, Grafana, Kubernetes, Helm, Jenkins, Redis, Docker, S3, PostgreSQL, Python, FastAPI, Yandex Cloud, Traefik.

<b>Инфраструктурная схема проекта:</b>
<img src="readme-pics/1.png"/>

Все приложения и инфраструктура создаются связкой Terraform и Ansible в облаке Yandex Cloud. Само микросервисное приложение находится в кластере Kubernetes.
Описание элементов данной схемы:
 - <b>Traefik(встроен в Kubernetes кластер).</b> Балансирует нагрузку на наше веб приложение.
 - <b>Kubernetes кластер.</b> Был выбран k3d для развертывания кластера Kubernetes. В нем работает само веб приложение, за обновление и развертывание которого отвечает Helm. Также он выдает метрики kube_state_metrics для сбора метрик Prometheus.
 - <b>Jenkins.</b> Совершает CI/CD приложения. Строит новые образы Docker, отправляет в DockerHub, совершает обновление приложения с помощью Helm стратегией Rolling update.
 - <b>Grafana.</b> Визуализирует метрики выдаваемые Prometheus
 - <b>Prometheus.</b> Собирает метрики от kube_state_metrics и node_exporter.
 - <b>S3 бакет</b> Хранит картинки для лотов, которые выставили пользователи.

<b>Архитектура приложения в кластере Kubernetes:</b>
<img src="readme-pics/2.png"/>

Описание элементов кластера Kubernetes:
 - **Backend service.**
   - Микросервис, отвечающий за взаимодействие с пользователем. Выдает веб страницу, подключает пользователя по WebSocket. Подключается к кластеру Redis, кластеру PostgreSQL, отправляет сообщения в RabbitMQ и хранит фото лотов в S3.<br/><br/>
 - **Auth service.**
   - Микросервис отвечающий за авторизацию/регистрацию пользователей. Подключается к кластеру Redis и кластеру PostgreSQL.<br/><br/>
 - **Crypto service.**
   - Микросервис, отвечающий за проверку настоящего баланса криптокошелька у пользователя. Подключается к одному из узлов децентрализованной сети Ethereum.<br/><br/>
 - **RabbitMQ от Bitnami.**
   - Передает асинхронные сообщения от Backend service в Telegram_Alerter. Возможно добавление и других способов рассылки.<br/><br/>
 - **Высокодоступный кластер Redis от Bitnami.**
   - Redis с включенной репликацией.<br/><br/>
 - **Высокодоступный кластер PostgreSQL от Bitnami.**
   - PostgreSQL с включенной репликацией. Общается с сервисами асинхронно.<br/><br/>
 - **Высокодоступный кластер PostgreSQL от Bitnami.**
   - PostgreSQL с включенной репликацией. Общается с сервисами асинхронно.<br/><br/>
 -  **Traefik.**
    - Балансирует нагрузку на Backend service.<br/><br/>
 - **Telegram_alerter service.**
   - Микросервис, отвечающий за рассылку о новых лотах всем, кто разрешил Telegram боту писать себе сообщения. Написан на aiogram.
    
## Скриншоты работы приложения:

### Страница авторизации.
<img src="readme-pics/3.jpg">

### Страница регистрации.
<img src="readme-pics/4.jpg">

### Отсутствие лотов для аукциона.
<img src="readme-pics/5.jpg">

### Страница добавления лота.
<img src="readme-pics/6.jpg">

### Процесс аукциона (Добавление к сумме в процентном отношении).
<img src="readme-pics/7.jpg">

### Рассылка от Telegram бота о новых лотах.
<img src="readme-pics/8.jpg">

## Планы развития проекта:

   - **Добавление Hashicorp Vault в архитектуру для удобной работы с секретами.**
   - **Развертывание кластера тестнета вместо crypto service и работа с ним.**
   - **Интеграция с Cryptomus или аналогами**