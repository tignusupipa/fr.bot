import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler,
    ContextTypes, ConversationHandler, MessageHandler, filters
)
from email.mime.text import MIMEText
import smtplib
from dotenv import load_dotenv

load_dotenv()

EMAIL_ADDRESS = os.getenv('EMAIL_ADDRESS')
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')
RECEIVER_EMAIL = os.getenv('RECEIVER_EMAIL')
BOT_TOKEN = os.getenv('BOT_TOKEN')

CHOOSING_CATEGORY, CHOOSING_PRODUCT, CHOOSING_QTY, CHOOSING_DETAILS, CONFIRMING, REQUESTING = range(6)

categories = {
    'tech': 'Tech',
    'maglie': 'Maglie da calcio attuali & retro',
    'profumi': 'Profumi',
    'sneakers': 'Sneakers',
    'abbigliamento': 'Abbigliamento di lusso & casual',
    'richieste': 'Richieste personalizzate'
}

products = {
    'tech': {
        'apple_watch_series_10': {
            'name': 'Apple Watch Series 10',
            'image': 'https://ysduwlxidmxq4xj3.public.blob.vercel-storage.com/apple-7Mt3hCk8q5ckGmpUui8vQySHNdjDgA.png'
        },
        'cuffie_sony_WH': {
            'name': 'Cuffie Sony WH-1000XM4',
            'image': 'https://fast-reseller.vercel.app/cuffie.jpg'
        },
        'apple_airpods_pro': {
            'name': 'Apple AirPods Pro',
            'image': 'https://fast-reseller.vercel.app/airpod.jpg'
        },
        'speaker_bluetooth_jbl': {
            'name': 'Speaker Bluetooth JBL',
            'image': 'https://fast-reseller.vercel.app/img/speaker.jpg'
        }
    },
    'maglie': {
        'manu_ronaldo_2007': {
            'name': 'Manchester United, Cristiano Ronaldo 2007 Champions League Final',
            'image': 'https://fast-reseller.vercel.app/img/Rinaldo3.jpg'
        },
        'milan_kaka_2007': {
            'name': "A.C Milan Kaká 2007 Champions League Final",
            'image': 'https://fast-reseller.vercel.app/img/kakaL.jpg'
        },
        'lamine_yamal': {
            'name': 'Lamine Yamal',
            'image': 'https://fast-reseller.vercel.app/img/lamine%20copertina.jpg'
        },
        'cristiano_ronaldo': {
            'name': 'Cristiano Ronaldo',
            'image': 'https://fast-reseller.vercel.app/img/IMG-20250701-WA0018.jpg'
        },
        'kvaratskhelia': {
            'name': 'Kvaratskhelia',
            'image': 'https://fast-reseller.vercel.app/img/IMG-20250701-WA0033.jpg'
        },
        'milan_maldini_2007': {
            'name': 'A.C Milan Maldini 2007 Champions League Final',
            'image': 'https://fast-reseller.vercel.app/img/maldini.jpg'
        }
    },
    'profumi': {
        'dior_homme': {
            'name': 'Dior Homme Intense',
            'image': 'https://fast-reseller.vercel.app/img/dior.jpg'
        },
        'chanel_5': {
            'name': 'Chanel N.5',
            'image': 'https://fast-reseller.vercel.app/img/n5.jpg'
        },
        'acqua_di_gio': {
            'name': 'Acqua di Giò',
            'image': 'https://fast-reseller.vercel.app/img/acqua.jpg'
        },
        'jean_paul': {
            'name': 'Jean Paul Gautier',
            'image': 'https://ysduwlxidmxq4xj3.public.blob.vercel-storage.com/Immagine%20WhatsApp%202025-07-07%20ore%2020.43.07_ff4a5b3c-rXYCQyAu58H1fN1sv04FKaqp1pdiVS.jpg'
        }
    },
    'sneakers': {
        'jordan_1': {
            'name': 'Jordan 1 Retro',
            'image': 'https://fast-reseller.vercel.app/img/1.jpg'
        },
        'nike_air_max': {
            'name': 'Nike Air Max',
            'image': 'https://fast-reseller.vercel.app/img/air.jpeg'
        },
        'yeezy_350': {
            'name': 'Yeezy Boost 350',
            'image': 'https://fast-reseller.vercel.app/img/3.webp'
        },
        'yeezy_350_v2_bone': {
            'name': 'Yeezy Boost 350 V2 Bone',
            'image': 'https://ysduwlxidmxq4xj3.public.blob.vercel-storage.com/350-5Gh053Z999svWQ2TRCukeGywAzfqdV.webp'
        },
        'air_force_1': {
            'name': 'Air Force 1 White',
            'image': 'https://ysduwlxidmxq4xj3.public.blob.vercel-storage.com/af1-eRBTU09PiDFMkont7lhtBUGOm6Vd5b.webp'
        }
    },
    'abbigliamento': {
        'ralph_maglietta': {
            'name': 'Maglietta Ralph Lauren',
            'image': 'https://fast-reseller.vercel.app/img/ralph.jpg'
        },
        'moncler_giacca': {
            'name': 'Giacca Moncler',
            'image': 'https://fast-reseller.vercel.app/img/moncler.webp'
        },
        'zara_tshirt': {
            'name': 'T-shirt Zara',
            'image': 'https://fast-reseller.vercel.app/img/t.jpg'
        },
        'dior_pochette': {
            'name': 'Pochette Dior',
            'image': 'https://ysduwlxidmxq4xj3.public.blob.vercel-storage.com/dior-dvdImqKKhRRKzJBn4dbWfak1Vn41qG.webp'
        },
        'lv_cintura': {
            'name': 'Cintura Louis Vuitton',
            'image': 'https://ysduwlxidmxq4xj3.public.blob.vercel-storage.com/louis-z6glbagvn5Nxqm4k1UYxiIes20toBZ.webp'
        }
    }
}

active_orders = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton(name, callback_data=key)] for key, name in categories.items()]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Benvenuto su FastReseller! Scegli una categoria:", reply_markup=reply_markup)
    return CHOOSING_CATEGORY

async def catalogo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton(name, callback_data=key)] for key, name in categories.items()]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Ecco il catalogo. Scegli una categoria:", reply_markup=reply_markup)
    return CHOOSING_CATEGORY

async def contatti(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "📞 *Contattaci*\n\n"
        "📧 Email: fastreseller10@gmail.com\n"
        "📸 Instagram: https://www.instagram.com/fastreseller\n"
        "🛒 Vinted: https://www.vinted.it/member/267598057-fastreseller10\n"
    )
    await update.message.reply_text(text, parse_mode='Markdown')

async def aiuto(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "💡 *Come usare FastReseller Bot*\n\n"
        "/start o /catalogo - Sfoglia le categorie e prodotti\n"
        "/ordina - Avvia un ordine guidato\n"
        "/contatti - Vedi i nostri recapiti\n"
        "/info - Informazioni sul negozio\n\n"
        "Se vuoi ordinare, scegli la categoria e poi il prodotto. Segui le istruzioni!\n"
        "Per richieste personalizzate, scegli la categoria 'Richieste personalizzate'."
    )
    await update.message.reply_text(text, parse_mode='Markdown')

async def info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "🏪 *Fast Reseller*\n"
        "Vendita di maglie da calcio, tech, profumi, sneakers e abbigliamento.\n"
        "Sito web: https://fastreseller.it\n"
        "Email: fastreseller10@gmail.com\n"
        "Seguici sui social per offerte e novità!"
    )
    await update.message.reply_text(text, parse_mode='Markdown')

async def choose_category(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    cat_key = query.data

    if cat_key == 'richieste':
        await query.edit_message_text("Scrivi qui la tua richiesta personalizzata:")
        return REQUESTING

    context.user_data['category'] = cat_key
    prod_list = products.get(cat_key, {})
    keyboard = [
        [InlineKeyboardButton(prod['name'], callback_data=key)] for key, prod in prod_list.items()
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(
        f"Hai scelto *{categories[cat_key]}*. Scegli un prodotto:",
        parse_mode='Markdown',
        reply_markup=reply_markup
    )
    return CHOOSING_PRODUCT

async def choose_product(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    prod_key = query.data
    cat_key = context.user_data.get('category')

    product = products[cat_key][prod_key]
    user_id = query.from_user.id
    first_name = query.from_user.first_name

    active_orders[user_id] = {
        'category': categories[cat_key],
        'product': product['name'],
        'product_image': product['image'],
        'user_id': user_id,
        'first_name': first_name
    }

    await query.edit_message_media(
        media=InputMediaPhoto(product['image'])
    )
    await query.message.reply_text(
        f"Hai scelto: *{product['name']}*\nQuante unità vuoi ordinare?",
        parse_mode='Markdown'
    )
    return CHOOSING_QTY

async def choose_qty(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    qty_text = update.message.text

    if not qty_text.isdigit() or int(qty_text) < 1:
        await update.message.reply_text("Inserisci un numero valido (es: 1, 2, 3).")
        return CHOOSING_QTY

    active_orders[user_id]['quantity'] = int(qty_text)
    await update.message.reply_text("Inserisci eventuali dettagli per la consegna, e l'indirizzo a cui spedire l'ordine(e le caratteristiche del prodotto)")
    return CHOOSING_DETAILS

async def choose_details(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    active_orders[user_id]['details'] = update.message.text
    order = active_orders[user_id]

    summary = (
        f"Riepilogo ordine:\n"
        f"Categoria: {order['category']}\n"
        f"Prodotto: {order['product']}\n"
        f"Quantità: {order['quantity']}\n"
        f"Dettagli: {order['details']}\n\n"
        "Confermi l'ordine? (si/no)"
    )
    await update.message.reply_text(summary)
    return CONFIRMING

async def confirm_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    text = update.message.text.lower()

    if text == 'si':
        order = active_orders.get(user_id)
        if order:
            send_order_email(order)
            await update.message.reply_text("✅ Ordine ricevuto! Ti contatteremo al più presto.")
            active_orders.pop(user_id)
        return ConversationHandler.END

    elif text == 'no':
        await update.message.reply_text("❌ Ordine annullato.")
        active_orders.pop(user_id, None)
        return ConversationHandler.END

    else:
        await update.message.reply_text("Rispondi solo con 'si' o 'no'.")
        return CONFIRMING

async def handle_request(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    text = update.message.text
    body = f"Richiesta da utente {user_id}:\n{text}"
    send_email("Richiesta FastReseller", body)
    await update.message.reply_text("Grazie! Ti risponderemo presto.")
    return ConversationHandler.END

def send_order_email(order):
    body = (
        f"🛒 Nuovo ordine da FastReseller Bot:\n\n"
        f"👤 Utente: {order['first_name']} (ID: {order['user_id']})\n"
        f"📦 Categoria: {order['category']}\n"
        f"📌 Prodotto: {order['product']}\n"
        f"🔢 Quantità: {order['quantity']}\n"
        f"📍 Dettagli: {order['details']}"
    )
    send_email("Nuovo ordine FastReseller", body)

def send_email(subject, body):
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = RECEIVER_EMAIL

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.sendmail(EMAIL_ADDRESS, RECEIVER_EMAIL, msg.as_string())
        server.quit()
        print("✅ Email inviata correttamente")
    except Exception as e:
        print(f"Errore invio email: {e}")

conv_handler = ConversationHandler(
    entry_points=[
        CommandHandler('start', start),
        CommandHandler('ordina', start),
        CommandHandler('catalogo', start)
    ],
    states={
        CHOOSING_CATEGORY: [CallbackQueryHandler(choose_category)],
        CHOOSING_PRODUCT: [CallbackQueryHandler(choose_product)],
        CHOOSING_QTY: [MessageHandler(filters.TEXT & ~filters.COMMAND, choose_qty)],
        CHOOSING_DETAILS: [MessageHandler(filters.TEXT & ~filters.COMMAND, choose_details)],
        CONFIRMING: [MessageHandler(filters.Regex('^(si|no)$'), confirm_order)],
        REQUESTING: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_request)],
    },
    fallbacks=[
        CommandHandler('start', start),
        CommandHandler('ordina', start),
        CommandHandler('catalogo', start)
    ]
)

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(conv_handler)
    app.add_handler(CommandHandler('catalogo', catalogo))
    app.add_handler(CommandHandler('contatti', contatti))
    app.add_handler(CommandHandler('aiuto', aiuto))
    app.add_handler(CommandHandler('info', info))
    app.run_polling()

if __name__ == '__main__':
    main()
