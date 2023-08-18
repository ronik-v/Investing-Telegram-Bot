# Investing-Telegram-Bot
<em>The program allows you to create an investment portfolio with maximum profitability and minimum risks, analyze the dynamics of prices for ordinary shares in real time, and keep abreast of financial news.</em><br>

<h3>What can this bot do?</h3>
<ul>
    <li>Get a visual representation of the current dynamics of stocks;</li>
    <li>Create an individual investment portfolio according to the given cost parameters;</li>
    <li>Make an optimal choice of assets based on the required ratio of profitability/risk.</li>
</ul>

<div>
    <p>Start command:</p><br>
    <img src="images/start.png"/><br>
</div>

<div>
<h3>Details:</h3>
<ul>
    <li>As a model for determining the structure of the investment portfolio, the model of G. Markowitz was chosen, according to which the portfolio with the minimum risk, the maximum Sharpe ratio and the average portfolio is determined.</li>
    <li>As information visualization are used:<br>
        1. Moving averages;<br>
        2. Japanese candles.</li>
    <li>Handled the situation with the attack of spam bots.</li>
</ul>
</div>

<div>
    <h3>Required to run bot</h3>
    <ul>
        <li>Create dir: Windows\Linux: <em>mkdir \Investing-Telegram-Bot\Graphs</li>
        <li>Install libs: aiogram, matplotlib, numpy, pandas_datareader</li>
        <li>Add your token in config.py</li>
    </ul>
</div>

<div>
    <h3>Examples</h3>
    <p>1. Creation of an investment portfolio: </p><br>
    <img src="images/portfolio.png"/><br>
    <p>2. Creating a graph: </p>
    <img src="images/graph.png"/>
</div>