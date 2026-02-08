
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler
from config import Config
from app.utils.google_sheets import get_revenue, get_sheet
import datetime

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 AI Business Partner Online.\n\n"
        "📋 Commands:\n"
        "/status - Check system status\n"
        "/revenue - Check total revenue\n"
        "/whatdidyoudotoday - View today's activity log\n"
        "/run - Research + Create a product\n\n"
        "🚀 V2 Commands:\n"
        "/publish - Publish product to Etsy/Pinterest\n"
        "/auth_etsy - Get Etsy authorization URL\n"
        "/auth_pinterest - Get Pinterest authorization URL"
    )

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Retrieve last activity from logs
    sheet = get_sheet()
    status_msg = "System Online. No logs found yet."
    if sheet:
        try:
            ws = sheet.worksheet("Activity Log")
            # Get last row (simplistic approach, might merit caching or optimized reading)
            # We'll read the last 5 rows to be safe
            all_values = ws.get_all_values()
            if len(all_values) > 1:
                last_entry = all_values[-1]
                # Timestamp, Agent, Action, Result
                status_msg = f"Last Action:\n{last_entry[0]}\n{last_entry[1]}: {last_entry[2]} - {last_entry[3]}"
        except Exception as e:
            status_msg = f"Error reading status: {e}"
    
    await update.message.reply_text(status_msg)

async def revenue(update: Update, context: ContextTypes.DEFAULT_TYPE):
    total = get_revenue()
    await update.message.reply_text(f"💰 Total Revenue Logged: ${total}")

async def whatdidyoudotoday(update: Update, context: ContextTypes.DEFAULT_TYPE):
    sheet = get_sheet()
    if not sheet:
        await update.message.reply_text("Memory error.")
        return

    try:
        ws = sheet.worksheet("Activity Log")
        all_values = ws.get_all_values()
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        
        # Filter for today (assuming ISO format YYYY-MM-DD...)
        todays_actions = [row for row in all_values[1:] if row[0].startswith(today)]
        
        if not todays_actions:
            await update.message.reply_text("No actions logged today.")
            return

        summary = "📊 Today's Activity:\n"
        for row in todays_actions[-10:]: # Show last 10 to avoid spam
            # Time (approx), Agent, Action
            time_part = row[0].split('T')[1].split('.')[0] if 'T' in row[0] else row[0]
            summary += f"[{time_part}] {row[1]}: {row[2]}\n"
        
        if len(todays_actions) > 10:
            summary += f"...and {len(todays_actions) - 10} more."

        await update.message.reply_text(summary)
    except Exception as e:
        await update.message.reply_text(f"Error fetching logs: {e}")

async def run_manual(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("⏳ Triggering manual run...")
    # This invokes the callback stored in context.bot_data if available
    if "manual_trigger" in context.bot_data:
        await context.bot_data["manual_trigger"](update, context)
    else:
        await update.message.reply_text("Manual trigger not configured.")

async def publish(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Publish latest product to Etsy and Pinterest."""
    await update.message.reply_text("🚀 Publishing to marketplaces...")
    
    if "publish_trigger" in context.bot_data:
        await context.bot_data["publish_trigger"](update, context)
    else:
        await update.message.reply_text("Publish trigger not configured.")

async def auth_etsy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Get Etsy OAuth URL."""
    from app.utils.etsy_api import get_auth_url
    auth_url, verifier = get_auth_url()
    await update.message.reply_text(
        f"🔐 Etsy Authorization\n\n"
        f"1. Visit this URL:\n{auth_url}\n\n"
        f"2. Save this verifier code:\n`{verifier}`\n\n"
        f"3. After authorizing, update .env with the access token."
    )

async def auth_pinterest(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Get Pinterest OAuth URL."""
    from app.utils.pinterest_api import get_auth_url
    auth_url = get_auth_url()
    await update.message.reply_text(
        f"🔐 Pinterest Authorization\n\n"
        f"Visit this URL:\n{auth_url}\n\n"
        f"After authorizing, update .env with the access token."
    )

def create_bot_app():
    if not Config.TELEGRAM_BOT_TOKEN:
        print("Telegram Token missing!")
        return None
        
    application = ApplicationBuilder().token(Config.TELEGRAM_BOT_TOKEN).build()
    
    # V1 Commands
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('status', status))
    application.add_handler(CommandHandler('revenue', revenue))
    application.add_handler(CommandHandler('whatdidyoudotoday', whatdidyoudotoday))
    application.add_handler(CommandHandler('run', run_manual))
    
    # V2 Commands
    application.add_handler(CommandHandler('publish', publish))
    application.add_handler(CommandHandler('auth_etsy', auth_etsy))
    application.add_handler(CommandHandler('auth_pinterest', auth_pinterest))
    
    return application
