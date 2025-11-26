# game_bot_inline.py
import telebot
import io
import textwrap
from telebot import types

# Bot tokeningizni shu yerga qo'ying

TOKEN = "8563036644:AAEG4I5mCwIdBOdIJ1q5ebcsmToFLSNO94w"
bot = telebot.TeleBot(TOKEN)
bot.remove_webhook()
# O'yinlar uchun HTML shablonlari
TEMPLATES = {
    "snake": textwrap.dedent("""\
        <!doctype html>
        <html>
        <head>
          <meta charset="utf-8">
          <title>Snake</title>
          <style>
            body { background:#111; color:#fff; display:flex; align-items:center; justify-content:center; height:100vh; margin:0; }
            canvas { background:#000; display:block; border:4px solid #222; }
          </style>
        </head>
        <body>
          <canvas id="c" width="400" height="400"></canvas>
          <script>
            const canvas = document.getElementById('c');
            const ctx = canvas.getContext('2d');
            const cell = 20;
            let dir = 'right';
            let snake = [{x:6,y:10},{x:5,y:10},{x:4,y:10}];
            let food = {x:10,y:7};

            document.addEventListener('keydown', e=>{
              if (e.key.includes('Arrow')) dir = e.key.replace('Arrow','').toLowerCase();
            });

            function draw(){
              ctx.clearRect(0,0,400,400);
              // food
              ctx.fillStyle = 'red';
              ctx.fillRect(food.x*cell, food.y*cell, cell, cell);

              // snake
              ctx.fillStyle = 'lime';
              snake.forEach(s => ctx.fillRect(s.x*cell, s.y*cell, cell-1, cell-1));

              // move
              const head = {x: snake[0].x, y: snake[0].y};
              if (dir==='right') head.x++;
              if (dir==='left') head.x--;
              if (dir==='up') head.y--;
              if (dir==='down') head.y++;

              // wall wrap
              head.x = (head.x+20) % 20;
              head.y = (head.y+20) % 20;

              // eat
              if(head.x===food.x && head.y===food.y){
                food = {x: Math.floor(Math.random()*20), y: Math.floor(Math.random()*20)};
              } else {
                snake.pop();
              }

              // collision with self
              if (snake.some(s=>s.x===head.x && s.y===head.y)) {
                alert('Game over! Refresh to play again.');
                snake = [{x:6,y:10},{x:5,y:10},{x:4,y:10}]; dir='right'; food={x:10,y:7};
              }

              snake.unshift(head);
            }

            setInterval(draw, 100);
          </script>
        </body>
        </html>
    """),
    "tic-tac-toe": textwrap.dedent("""\
        <!doctype html>
        <html>
        <head>
          <meta charset="utf-8">
          <title>Tic Tac Toe</title>
          <style>
            body{display:flex;align-items:center;justify-content:center;height:100vh;margin:0;background:#f3f3f3}
            #board{display:grid;grid-template-columns:repeat(3,120px);grid-gap:5px}
            .cell{width:120px;height:120px;background:#fff;display:flex;align-items:center;justify-content:center;font-size:48px;cursor:pointer}
            #msg{position:absolute;top:10px;font-family:sans-serif}
          </style>
        </head>
        <body>
          <div id="msg">X ning navbati</div>
          <div id="board"></div>
          <script>
            const boardEl = document.getElementById('board');
            const msg = document.getElementById('msg');
            let board = Array(9).fill(null);
            let turn = 'X';

            function render(){
              boardEl.innerHTML = '';
              board.forEach((v,i)=>{
                const cell = document.createElement('div');
                cell.className='cell';
                cell.textContent = v || '';
                cell.onclick = ()=> {
                  if (v || checkWinner()) return;
                  board[i] = turn;
                  turn = turn==='X'?'O':'X';
                  msg.textContent = turn + " ning navbati";
                  render();
                  const w = checkWinner();
                  if (w) setTimeout(()=>alert(w + " yutdi!"), 10);
                };
                boardEl.appendChild(cell);
              });
            }

            function checkWinner(){
              const win = [
                [0,1,2],[3,4,5],[6,7,8],
                [0,3,6],[1,4,7],[2,5,8],
                [0,4,8],[2,4,6]
              ];
              for (const w of win){
                const [a,b,c]=w;
                if (board[a] && board[a]===board[b] && board[b]===board[c]) return board[a];
              }
              if (board.every(Boolean)) return 'Hech kim';
              return null;
            }

            render();
          </script>
        </body>
        </html>
    """),
    "pong": textwrap.dedent("""\
        <!doctype html>
        <html>
        <head>
          <meta charset="utf-8">
          <title>Pong</title>
          <style>
            body{display:flex;align-items:center;justify-content:center;height:100vh;margin:0;background:#000}
            canvas{background:#111;border:2px solid #333}
          </style>
        </head>
        <body>
          <canvas id="c" width="600" height="400"></canvas>
          <script>
            const canvas = document.getElementById('c');
            const ctx = canvas.getContext('2d');
            const paddle = {w:10,h:80};
            let leftY = 160, rightY = 160;
            const ball = {x:300,y:200, vx:3, vy:3, r:8};

            document.addEventListener('mousemove', e=>{
              const rect = canvas.getBoundingClientRect();
              leftY = e.clientY - rect.top - paddle.h/2;
            });

            function draw(){
              ctx.clearRect(0,0,600,400);
              // paddles
              ctx.fillStyle='white';
              ctx.fillRect(10,leftY,paddle.w,paddle.h);
              ctx.fillRect(580,rightY,paddle.w,paddle.h);
              // ball
              ctx.beginPath();
              ctx.arc(ball.x,ball.y,ball.r,0,Math.PI*2);
              ctx.fill();

              // move ball
              ball.x += ball.vx; ball.y += ball.vy;

              // top/bottom
              if(ball.y<ball.r || ball.y>400-ball.r) ball.vy *= -1;

              // left paddle
              if(ball.x - ball.r < 20 && ball.y > leftY && ball.y < leftY + paddle.h) ball.vx *= -1;
              // right paddle (simple AI)
              if(ball.x + ball.r > 580 && ball.y > rightY && ball.y < rightY + paddle.h) ball.vx *= -1;

              // AI move
              if(rightY + paddle.h/2 < ball.y) rightY += 2; else rightY -= 2;

              // score / reset
              if(ball.x < 0 || ball.x > 600){
                ball.x = 300; ball.y = 200; ball.vx = 3 * (ball.vx<0?-1:1);
              }
            }

            setInterval(draw, 16);
          </script>
        </body>
        </html>
    """),
    "flappy-bird": textwrap.dedent("""\
        <!doctype html>
        <html>
        <head>
          <meta charset="utf-8">
          <title>Flappy</title>
          <style>
            body{display:flex;align-items:center;justify-content:center;height:100vh;margin:0;background: #70c5ce}
            canvas{background:#70c5ce;border:4px solid #2b7a78}
          </style>
        </head>
        <body>
          <canvas id="c" width="320" height="480"></canvas>
          <script>
            const c=document.getElementById('c'), ctx=c.getContext('2d');
            let bird={x:60,y:240,vy:0};
            let pipes=[];
            let frame=0;
            document.addEventListener('keydown', ()=> bird.vy = -6);
            function loop(){
              frame++;
              bird.vy += 0.3; bird.y += bird.vy;
              if(frame % 90 === 0){
                const gap = 120;
                const top = Math.random() * (c.height - gap - 60) + 20;
                pipes.push({x: c.width, top});
              }
              ctx.clearRect(0,0,c.width,c.height);
              // bird
              ctx.fillStyle='yellow'; ctx.fillRect(bird.x-12,bird.y-12,24,24);
              // pipes
              ctx.fillStyle='green';
              for(let i=pipes.length-1;i>=0;i--){
                const p=pipes[i]; p.x -= 2;
                ctx.fillRect(p.x, 0, 40, p.top);
                ctx.fillRect(p.x, p.top+120, 40, c.height - p.top - 120);
                if(p.x + 40 < 0) pipes.splice(i,1);
              }
              // collision
              for(const p of pipes){
                if(bird.x+12 > p.x && bird.x-12 < p.x+40){
                  if(bird.y-12 < p.top || bird.y+12 > p.top+120){
                    alert('Game Over. Refresh to play again.'); pipes = []; bird = {x:60,y:240,vy:0}; frame = 0;
                  }
                }
              }
              if(bird.y > c.height || bird.y < 0){ bird = {x:60,y:240,vy:0}; pipes = []; frame = 0; }
              requestAnimationFrame(loop);
            }
            loop();
          </script>
        </body>
        </html>
    """),
}

GENERIC_TEMPLATE = textwrap.dedent("""\
<!doctype html>
<html>
<head>
<meta charset="utf-8">
<title>{name}</title>
</head>
<body>
<h1>{name}</h1>
<p>Bu umumiy shablon.</p>
</body>
</html>
""")

def make_file_bytes(name: str, html: str):
    bio = io.BytesIO()
    bio.write(html.encode('utf-8'))
    bio.seek(0)
    filename = f"{name.replace(' ','_').lower()}.html"
    return bio, filename

# /start komandasi
@bot.message_handler(commands=['start','help'])
def send_welcome(message):
    kb = types.InlineKeyboardMarkup(row_width=2)
    btns = [
        types.InlineKeyboardButton("Snake", callback_data="snake"),
        types.InlineKeyboardButton("Tic Tac Toe", callback_data="tic-tac-toe"),
        types.InlineKeyboardButton("Pong", callback_data="pong"),
        types.InlineKeyboardButton("Flappy Bird", callback_data="flappy-bird"),
    ]
    kb.add(*btns)
    bot.send_message(
        message.chat.id,
        "Salom! 🎮\n\nQuyidagi tugmalardan o‘yin tanlang:",
        reply_markup=kb
    )

# Inline tugma bosilganda (o'yin tanlash)
@bot.callback_query_handler(func=lambda call: call.data in TEMPLATES.keys())
def game_handler(call):
    key = call.data
    bot.answer_callback_query(call.id)

    html = TEMPLATES[key]
    bio, filename = make_file_bytes(key, html)
    bot.send_document(call.message.chat.id, bio, visible_file_name=filename)

    # O'yindan keyin foydalanuvchiga savol
    kb2 = types.InlineKeyboardMarkup(row_width=2)
    btn_yes = types.InlineKeyboardButton("Xa", url="https://t.me/DeveloperMuhammad")  # sizning link
    btn_no = types.InlineKeyboardButton("Yuq", callback_data="no_web")
    kb2.add(btn_yes, btn_no)
    bot.send_message(call.message.chat.id, "Siz ham web dasturlashni o‘rganishni xohlaysizmi?", reply_markup=kb2)

# "Yuq" tugmasi handleri
@bot.callback_query_handler(func=lambda call: call.data=="no_web")
def no_web_handler(call):
    bot.answer_callback_query(call.id)
    bot.send_message(call.message.chat.id, "Sog‘ bo‘ling! 🙂")  # faqat matn

if __name__ == "__main__":
    print("Bot ishga tushdi...")
    bot.polling(none_stop=True)