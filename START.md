# Bot setup
<div>
    <ul>
        <div class="wrapper">
            <li><h3>Copy the repository</h3>
            <pre>git clone https://github.com/ronik-v/Investing-Telegram-Bot</pre></li>
            <li>
                <h3>Create directory</h3>
                <pre>mkdir src/Graphs</pre>
            </li>
            <li>
                <h3>Run the Investing-Bot project setup</h3>
                <pre>python3 setup.py install</pre>
            </li>
            <li>
                <h3>Libraries to install</h3>
                <pre>pip install -r requirements.txt</pre>
            </li>
            <li>
                <h3>Use dockerfile</h3>
                <pre>docker build -t docker-whale .</pre>
            </li>
            <li>
                <h3>Redis</h3>
                <p>If you want to change the Redis IP address and port, don't forget to change the connection in src/main.py</p>
            </li>
        </div>
    </ul>
</div>