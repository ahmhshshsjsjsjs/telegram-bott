from telegram import Update, LabeledPrice
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, PreCheckoutQueryHandler, MessageHandler, filters
import os
import paramiko

TOKEN = os.getenv("8558642201:AAHf0WGbZap5hC8NleMSB70hK39Rd5Bp4YY")

SSH_HOST = os.getenv("SSH_HOST")
SSH_USER = os.getenv("SSH_USER")
SSH_PASS = os.getenv("SSH_PASS")

user_ids = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Premium almak için:\n/buy OYUNCU_ID")

async def buy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) == 0:
        await update.message.reply_text("Kullanım: /buy OYUNCU_ID")
        return

    player_id = context.args[0]
    user_ids[update.effective_user.id] = player_id

    prices = [LabeledPrice("Premium", 100)]
    await context.bot.send_invoice(
        chat_id=update.effective_chat.id,
        title="Premium",
        description=f"Oyuncu ID: {player_id}",
        payload="premium",
        currency="XTR",
        prices=prices,
    )

async def precheckout(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.pre_checkout_query.answer(ok=True)

def give_premium(player_id):
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(SSH_HOST, username=SSH_USER, password=SSH_PASS)

        command = f"/premium add {player_id}"
        ssh.exec_command(command)

        ssh.close()
    except Exception as e:
        print("SSH Hata:", e)

async def success(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    player_id = user_ids.get(user_id)

    if player_id:
        give_premium(player_id)
        await update.message.reply_text("Ödeme başarılı! Premium verildi.")
    else:
        await update.message.reply_text("Ödeme alındı ama ID bulunamadı.")

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("buy", buy))
app.add_handler(PreCheckoutQueryHandler(precheckout))
app.add_handler(MessageHandler(filters.SUCCESSFUL_PAYMENT, success))

app.run_polling()
