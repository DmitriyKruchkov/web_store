

        const priceCurrent = document.getElementById('current-price');
        const priceInput = document.getElementById('new-price');

        function getCookie(name) {
            const value = `; ${document.cookie}`;
            const parts = value.split(`; ${name}=`);
            if (parts.length === 2) return parts.pop().split(';').shift();
    }
          const token = getCookie('access_token');
          const ws = new WebSocket(`ws://${window.location.host}/ws?access_token=${token}`);
            function updatePrice(newPrice) {
        const priceElement = document.getElementById('current-price');


        priceElement.textContent = newPrice;


        priceElement.style.color = 'green';


        setTimeout(() => {
            priceElement.style.color = '';
        }, 2000);
    }
        ws.onmessage = function(event) {

            const data = JSON.parse(event.data);
            console.log(data);
            document.getElementById('owner').innerText = data.address;
            updatePrice(data.price);


        };
        ws.onclose = function(event) {
            window.location.href = '/login';
        };
        function updateClock(timezone) {
            const clockElement = document.getElementById('clock');
            const now = new Date();
            const options = {
                timeZone: timezone,
                day: '2-digit',
                month: '2-digit',
                year: '2-digit',
                hour: '2-digit',
                minute: '2-digit',
                second: '2-digit',
                hour12: false
            };
            const formatter = new Intl.DateTimeFormat([], options);
            const formattedTime = formatter.format(now);
            clockElement.textContent = formattedTime;
        }

        // Укажите часовой пояс
        const timezone = 'Europe/Moscow';

        // Обновление времени каждую секунду
        setInterval(() => updateClock(timezone), 1000);

        // Начальная установка времени при загрузке страницы
        updateClock(timezone);

        function placeBid() {
            const input = document.getElementById("new-price");
            const newPrice = input.value;
            ws.send(newPrice);
            input.value = 5;
        }

        // Добавляем обработчики для кнопок
        document.getElementById('decrement').addEventListener('click', () => {
            let currentValue = parseInt(priceInput.value);
            if (currentValue > 5) {
                priceInput.value = currentValue - 5;
            }
        });

        document.getElementById('increment').addEventListener('click', () => {
            let currentValue = parseInt(priceInput.value);
            if (currentValue < 100) {
                priceInput.value = currentValue + 5;

            }
        });

