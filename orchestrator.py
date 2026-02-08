
import asyncio
import logging
from app.agents.research_agent import ResearchAgent
from app.agents.creation_agent import CreationAgent
from app.agents.publishing_agent import PublishingAgent
from app.utils.telegram_bot import create_bot_app
from app.utils.google_sheets import log_activity, setup_tabs

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def business_cycle(update=None, context=None):
    """
    Main business logic cycle:
    1. Research trends
    2. pick best trend
    3. Create product
    """
    logger.info("Starting business cycle...")
    log_activity("Orchestrator", "Start", "Scheduled Run Started")

    # 1. Research
    researcher = ResearchAgent()
    trends = researcher.run()

    if not trends:
        logger.info("No trends found.")
        log_activity("Orchestrator", "End", "No trends found")
        msg = "❌ No trends found."
    else:
        # 2. Pick best trend (top signal)
        best_trend = trends[0]
        logger.info(f"Top trend: {best_trend['keyword']}")

        # 3. Create Product
        creator = CreationAgent()
        product_link = creator.run(best_trend)

        if product_link:
            msg = f"✅ New Product Created!\n📝 Keyword: {best_trend['keyword']}\n🔗 Link: {product_link}"
        else:
            msg = f"❌ Failed to create product for {best_trend['keyword']}"

    log_activity("Orchestrator", "End", "Cycle Complete")
    
    # Notify via Telegram
    if update:
        await update.message.reply_text(msg)
    elif context and context.job:
        await context.bot.send_message(chat_id=context.job.chat_id, text=msg)


async def publish_cycle(update=None, context=None, platform="both"):
    """
    Publish latest product to marketplaces.
    """
    logger.info("Starting publish cycle...")
    
    publisher = PublishingAgent()
    results = publisher.run(platform=platform)
    
    if not results.get("success", True):
        msg = f"❌ {results.get('message', 'Publishing failed')}"
    else:
        msg = f"📦 Publishing Results for: {results.get('product_name', 'Unknown')}\n\n"
        
        # Etsy results
        etsy = results.get("etsy")
        if etsy:
            if etsy.get("success"):
                msg += f"✅ Etsy: {etsy.get('url', 'Created')}\n"
            else:
                msg += f"❌ Etsy: {etsy.get('error', 'Failed')}\n"
        
        # Pinterest results
        pinterest = results.get("pinterest")
        if pinterest:
            if pinterest.get("success"):
                msg += f"✅ Pinterest: {pinterest.get('url', 'Created')}\n"
            else:
                msg += f"❌ Pinterest: {pinterest.get('error', 'Failed')}\n"
    
    # Notify via Telegram
    if update:
        await update.message.reply_text(msg)


if __name__ == "__main__":
    # Ensure sheet tabs exist
    setup_tabs()

    # Create Bot Application
    application = create_bot_app()

    if not application:
        print("Failed to initialize Bot. Check config.")
        exit(1)

    # Register manual trigger for /run command
    async def manual_wrapper(update, context):
        await business_cycle(update=update, context=context)

    application.bot_data["manual_trigger"] = manual_wrapper

    # Register publish trigger for /publish command
    async def publish_wrapper(update, context):
        await publish_cycle(update=update, context=context)

    application.bot_data["publish_trigger"] = publish_wrapper

    # Start the bot
    print("🤖 AI Business Partner Orchestrator is running...")
    print("Commands available: /run, /publish, /status, /revenue")
    print("Press Ctrl+C to stop.")
    
    application.run_polling()
