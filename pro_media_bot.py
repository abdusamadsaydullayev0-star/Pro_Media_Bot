Content is user-generated and unverified.
import logging
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    MessageHandler, filters, ContextTypes, ConversationHandler
)
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from datetime import datetime
import os

BOT_TOKEN = "8708467547:AAG2SM-aNDgFEhCSjKurDB3YHXmWtcYB3Cs"
ADMIN_ID = 8340818638

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

(
    MAIN_MENU, ORDER_VIDEO_COUNT, ORDER_WAIT_PRICE, ORDER_CONFIRM,
    CONTRACT_ISM, CONTRACT_FAMILYA, CONTRACT_PHONE, CONTRACT_XIZMAT,
    CONTRACT_SUMMA, CONTRACT_MUDDAT, CONTRACT_CONFIRM,
) = range(11)

user_data_store = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    keyboard = [
        [InlineKeyboardButton("📁 Portfolio ko'rish", callback_data="portfolio")],
        [InlineKeyboardButton("💰 Narx-navo", callback_data="narx")],
        [InlineKeyboardButton("📄 Shartnoma tuzish", callback_data="shartnoma")],
        [InlineKeyboardButton("📞 Bog'lanish", callback_data="boglanish")],
    ]
    await update.message.reply_text(
        f"👋 Salom, {user.first_name}!\n\n"
        "🎬 *Pro Media* — Professional SMM & Mobilografiya xizmatlari\n\n"
        "Quyidagi bo'limlardan birini tanlang:",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )
    return MAIN_MENU

async def portfolio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    keyboard = [[InlineKeyboardButton("🔙 Orqaga", callback_data="back_main")]]
    await query.edit_message_text(
        "📁 *Portfolio*\n\n"
        "🎬 Bizning ishlarimiz:\n\n"
        "📱 Instagram: @pro_media_uz\n"
        "▶️ YouTube: Pro Media UZ\n"
        "🎥 TikTok: @promedia_uz\n\n"
        "💼 Xizmatlar:\n"
        "• Mobil videografiya\n"
        "• SMM boshqaruvi\n"
        "• Reels & Short video\n"
        "• Kontent rejasi",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )

async def narx(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    keyboard = [
        [InlineKeyboardButton("🛒 Xizmat buyurtma qilish", callback_data="buyurtma")],
        [InlineKeyboardButton("🔙 Orqaga", callback_data="back_main")],
    ]
    await query.edit_message_text(
        "💰 *Narx-navo*\n\n"
        "📹 Video narxlari (1 oylik):\n\n"
        "10-12 ta video: $250-300\n"
        "13-15 ta video: $300-350\n"
        "16-20 ta video: $350-450\n\n"
        "📌 *1 ta video narxi:* $20\n\n"
        "⏳ Shartnoma muddatlari: 3 oy, 6 oy, 12 oy",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )

async def buyurtma(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    user_data_store[user_id] = {}
    await query.edit_message_text(
        "🛒 *Xizmat buyurtma qilish*\n\n"
        "📹 Har oyda nechta video kerak?\n\nMasalan: 12",
        parse_mode="Markdown"
    )
    return ORDER_VIDEO_COUNT

async def order_video_count(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text.strip()
    if not text.isdigit():
        await update.message.reply_text("❌ Iltimos, faqat raqam kiriting. Masalan: 12")
        return ORDER_VIDEO_COUNT
    video_count = int(text)
    user_data_store[user_id] = {
        "video_count": video_count,
        "user_name": update.effective_user.full_name,
        "user_username": update.effective_user.username or "yoq",
        "user_id": user_id,
    }
    await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=f"🔔 *Yangi buyurtma!*\n\n"
             f"👤 Mijoz: {update.effective_user.full_name}\n"
             f"🆔 Username: @{update.effective_user.username or 'yoq'}\n"
             f"🆔 ID: `{user_id}`\n"
             f"📹 Video soni: *{video_count} ta/oy*\n\n"
             f"Narx yuborish uchun:\n`/narx_{user_id}_SUMMA`\nMasalan: `/narx_{user_id}_300`",
        parse_mode="Markdown"
    )
    await update.message.reply_text(
        f"✅ *So'rovingiz qabul qilindi!*\n\n"
        f"📹 Video soni: *{video_count} ta/oy*\n\n"
        f"⏳ Administrator narxni tasdiqlaydi...",
        parse_mode="Markdown"
    )
    return ORDER_WAIT_PRICE

async def admin_narx(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    try:
        parts = update.message.text.split("_")
        target_user_id = int(parts[1])
        summa = parts[2]
        user_data_store[target_user_id]["taklif_narx"] = summa
        keyboard = [[
            InlineKeyboardButton("✅ Roziman", callback_data=f"confirm_yes_{target_user_id}"),
            InlineKeyboardButton("❌ Rad etaman", callback_data=f"confirm_no_{target_user_id}"),
        ]]
        await context.bot.send_message(
            chat_id=target_user_id,
            text=f"💰 *Narx taklifi!*\n\n"
                 f"📹 Video soni: *{user_data_store[target_user_id].get('video_count', '?')} ta/oy*\n"
                 f"💵 Taklif narx: *${summa}/oy*\n\nQabul qilasizmi?",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )
        await update.message.reply_text(f"✅ Narx ${summa} mijozga yuborildi!")
    except Exception as e:
        await update.message.reply_text(f"❌ Xato: {e}\nFormat: /narx_ID_SUMMA")

async def confirm_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    if data.startswith("confirm_yes_"):
        target_id = int(data.split("_")[2])
        narx_s = user_data_store.get(target_id, {}).get("taklif_narx", "?")
        video_count = user_data_store.get(target_id, {}).get("video_count", "?")
        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=f"✅ *Mijoz narxni qabul qildi!*\n👤 ID: `{target_id}`\n💵 ${narx_s}/oy\n📹 {video_count} ta/oy",
            parse_mode="Markdown"
        )
        keyboard = [[InlineKeyboardButton("📄 Shartnoma tuzish", callback_data="shartnoma")]]
        await query.edit_message_text(
            f"✅ *Kelishildi!*\n\n💵 Narx: *${narx_s}/oy*\n\nShartnoma tuzish uchun tugmani bosing:",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )
    elif data.startswith("confirm_no_"):
        target_id = int(data.split("_")[2])
        await context.bot.send_message(chat_id=ADMIN_ID, text=f"❌ Mijoz ({target_id}) narxni rad etdi.")
        await query.edit_message_text("❌ Tushunildi. Bog'lanish uchun adminga murojaat qiling.")

async def shartnoma_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.callback_query.from_user.id if update.callback_query else update.effective_user.id
    if update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.edit_message_text(
            "📄 *Shartnoma tuzish*\n\n👤 Ismingizni kiriting:\n_(Masalan: Jasur)_",
            parse_mode="Markdown"
        )
    else:
        await update.message.reply_text(
            "📄 *Shartnoma tuzish*\n\n👤 Ismingizni kiriting:",
            parse_mode="Markdown"
        )
    if user_id not in user_data_store:
        user_data_store[user_id] = {}
    user_data_store[user_id]["contract"] = {}
    return CONTRACT_ISM

async def contract_ism(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_data_store[user_id]["contract"]["ism"] = update.message.text.strip()
    await update.message.reply_text("👤 Familyangizni kiriting:\n_(Masalan: Toshmatov)_", parse_mode="Markdown")
    return CONTRACT_FAMILYA

async def contract_familya(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_data_store[user_id]["contract"]["familya"] = update.message.text.strip()
    await update.message.reply_text("📞 Telefon raqamingizni kiriting:\n_(Masalan: +998901234567)_", parse_mode="Markdown")
    return CONTRACT_PHONE

async def contract_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_data_store[user_id]["contract"]["phone"] = update.message.text.strip()
    keyboard = [
        [InlineKeyboardButton("🎬 SMM + Video", callback_data="xizmat_smm_video")],
        [InlineKeyboardButton("📱 Faqat Video", callback_data="xizmat_video")],
        [InlineKeyboardButton("📊 SMM Boshqaruv", callback_data="xizmat_smm")],
    ]
    await update.message.reply_text("💼 Xizmat turini tanlang:", reply_markup=InlineKeyboardMarkup(keyboard))
    return CONTRACT_XIZMAT

async def contract_xizmat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    xizmat_map = {
        "xizmat_smm_video": "SMM + Mobil Videografiya",
        "xizmat_video": "Mobil Videografiya",
        "xizmat_smm": "SMM Boshqaruv",
    }
    user_data_store[user_id]["contract"]["xizmat"] = xizmat_map[query.data]
    await query.edit_message_text("💵 Kelishilgan summani kiriting ($):\n_(Masalan: 300)_", parse_mode="Markdown")
    return CONTRACT_SUMMA

async def contract_summa(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text.strip().replace("$", "").replace(" ", "")
    if not text.replace(".", "").isdigit():
        await update.message.reply_text("❌ Faqat raqam kiriting. Masalan: 300")
        return CONTRACT_SUMMA
    user_data_store[user_id]["contract"]["summa"] = text
    keyboard = [
        [InlineKeyboardButton("📅 3 oylik", callback_data="muddat_3")],
        [InlineKeyboardButton("📅 6 oylik", callback_data="muddat_6")],
        [InlineKeyboardButton("📅 12 oylik", callback_data="muddat_12")],
    ]
    await update.message.reply_text("⏳ Shartnoma muddatini tanlang:", reply_markup=InlineKeyboardMarkup(keyboard))
    return CONTRACT_MUDDAT

async def contract_muddat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    muddat_map = {"muddat_3": "3 oy", "muddat_6": "6 oy", "muddat_12": "12 oy"}
    user_data_store[user_id]["contract"]["muddat"] = muddat_map[query.data]
    c = user_data_store[user_id]["contract"]
    oylik = float(c["summa"])
    muddat_raqam = int(query.data.split("_")[1])
    jami = oylik * muddat_raqam
    user_data_store[user_id]["contract"]["jami"] = str(jami)
    user_data_store[user_id]["contract"]["oldindan"] = str(oylik)
    keyboard = [[
        InlineKeyboardButton("✅ Tasdiqlash", callback_data="contract_confirm"),
        InlineKeyboardButton("❌ Bekor", callback_data="back_main"),
    ]]
    await query.edit_message_text(
        f"📄 *Shartnoma ma'lumotlari:*\n\n"
        f"👤 {c['ism']} {c['familya']}\n"
        f"📞 {c['phone']}\n"
        f"💼 {c['xizmat']}\n"
        f"💵 Oylik: ${c['summa']}\n"
        f"⏳ Muddat: {c['muddat']}\n"
        f"💰 Jami: ${jami}\n"
        f"🔐 Oldindan: ${oylik}\n\n"
        f"Ma'lumotlar to'g'rimi?",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )
    return CONTRACT_CONFIRM

async def contract_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    await query.edit_message_text("⏳ PDF shartnoma tayyorlanmoqda...")
    c = user_data_store[user_id]["contract"]
    pdf_path = generate_contract_pdf(c, user_id)
    with open(pdf_path, "rb") as f:
        await context.bot.send_document(
            chat_id=user_id,
            document=f,
            filename=f"Shartnoma_{c['ism']}_{c['familya']}.pdf",
            caption=f"✅ *Shartnomangiz tayyor!*\n\n🖨️ Chop etib, imzo qo'ying.\n💵 Oldindan to'lov: *${c['oldindan']}*",
            parse_mode="Markdown"
        )
    with open(pdf_path, "rb") as f:
        await context.bot.send_document(
            chat_id=ADMIN_ID,
            document=f,
            filename=f"Shartnoma_{c['ism']}_{c['familya']}.pdf",
            caption=f"📄 *Yangi shartnoma!*\n\n👤 {c['ism']} {c['familya']}\n📞 {c['phone']}\n💵 ${c['summa']}/oy | {c['muddat']}\n💰 Jami: ${c['jami']}",
            parse_mode="Markdown"
        )
    os.remove(pdf_path)
    return MAIN_MENU

def generate_contract_pdf(c, user_id):
    filename = f"contract_{user_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf"
    doc = SimpleDocTemplate(filename, pagesize=A4, rightMargin=2*cm, leftMargin=2*cm, topMargin=2*cm, bottomMargin=2*cm)
    styles = getSampleStyleSheet()
    story = []
    title_style = ParagraphStyle('title', parent=styles['Normal'], fontSize=16, fontName='Helvetica-Bold', alignment=TA_CENTER, spaceAfter=6)
    normal_style = ParagraphStyle('normal', parent=styles['Normal'], fontSize=10, fontName='Helvetica', spaceAfter=4, leading=16)
    heading_style = ParagraphStyle('heading', parent=styles['Normal'], fontSize=11, fontName='Helvetica-Bold', spaceBefore=12, spaceAfter=4)
    today = datetime.now()
    date_str = today.strftime("%d.%m.%Y")
    story.append(Paragraph("XIZMAT KO'RSATISH SHARTNOMASI", title_style))
    story.append(Spacer(1, 0.3*cm))
    story.append(HRFlowable(width="100%", thickness=2, color=colors.black))
    story.append(Spacer(1, 0.3*cm))
    story.append(Paragraph(f"Sana: {date_str}    Shartnoma: PM-{today.strftime('%Y%m%d')}-{user_id % 1000:03d}", normal_style))
    story.append(Spacer(1, 0.3*cm))
    story.append(Paragraph("TOMONLAR", heading_style))
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.grey))
    parties_data = [
        ["IJROCHI:", "Pro Media", "BUYURTMACHI:", f"{c['ism']} {c['familya']}"],
        ["Telegram:", "@ProMediaAdmin_bot", "Telefon:", c['phone']],
        ["", "", "Imzo:", "_______________"],
    ]
    parties_table = Table(parties_data, colWidths=[3.5*cm, 6*cm, 3.5*cm, 6*cm])
    parties_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
    ]))
    story.append(parties_table)
    story.append(Spacer(1, 0.4*cm))
    story.append(Paragraph("SHARTNOMA TAFSILOTLARI", heading_style))
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.grey))
    story.append(Spacer(1, 0.2*cm))
    details_data = [
        ["Xizmat:", c['xizmat']],
        ["Muddat:", c['muddat']],
        ["Boshlash:", date_str],
    ]
    details_table = Table(details_data, colWidths=[4*cm, 13*cm])
    details_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(details_table)
    story.append(Spacer(1, 0.4*cm))
    story.append(Paragraph("TO'LOV SHARTLARI", heading_style))
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.grey))
    payment_data = [
        ["TO'LOV TURI", "SUMMA"],
        ["Oylik to'lov", f"${c['summa']}"],
        ["Jami summa", f"${c['jami']}"],
        ["OLDINDAN TO'LOV", f"${c['oldindan']}"],
    ]
    payment_table = Table(payment_data, colWidths=[10*cm, 7*cm])
    payment_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.black),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('BACKGROUND', (0, -1), (-1, -1), colors.Color(0.9, 0.95, 0.9)),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 7),
        ('TOPPADDING', (0, 0), (-1, -1), 7),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ]))
    story.append(payment_table)
    story.append(Spacer(1, 0.5*cm))
    story.append(Paragraph("SHARTLAR", heading_style))
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.grey))
    for s in [
        "1. Ijrochi kelishilgan miqdorda sifatli kontent tayyorlaydi.",
        "2. Buyurtmachi har oy belgilangan miqdorda to'lov qiladi.",
        "3. Oldindan to'lovdan so'ng ish boshlanadi.",
        "4. Shartnomani bekor qilish uchun 15 kun oldin xabar berish shart.",
    ]:
        story.append(Paragraph(s, normal_style))
    story.append(Spacer(1, 0.5*cm))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.black))
    story.append(Spacer(1, 0.3*cm))
    sign_data = [["IJROCHI", "", "BUYURTMACHI"], ["Pro Media", "", f"{c['ism']} {c['familya']}"], ["Imzo: ___________", "", "Imzo: ___________"], [date_str, "", date_str]]
    sign_table = Table(sign_data, colWidths=[7*cm, 3*cm, 7*cm])
    sign_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTNAME', (0, 0), (0, 0), 'Helvetica-Bold'),
        ('FONTNAME', (2, 0), (2, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('ALIGN', (2, 0), (2, -1), TA_RIGHT),
    ]))
    story.append(sign_table)
    doc.build(story)
    return filename

async def boglanish(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    keyboard = [[InlineKeyboardButton("🔙 Orqaga", callback_data="back_main")]]
    await query.edit_message_text(
        "📞 *Bog'lanish*\n\n👤 Admin: @ProMediaAdmin\n📱 Telefon: +998 XX XXX XX XX\n\n_Ish vaqti: 09:00 - 22:00_",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )

async def back_main(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    keyboard = [
        [InlineKeyboardButton("📁 Portfolio ko'rish", callback_data="portfolio")],
        [InlineKeyboardButton("💰 Narx-navo", callback_data="narx")],
        [InlineKeyboardButton("📄 Shartnoma tuzish", callback_data="shartnoma")],
        [InlineKeyboardButton("📞 Bog'lanish", callback_data="boglanish")],
    ]
    await query.edit_message_text(
        "🏠 *Asosiy menyu*\n\n🎬 *Pro Media* — Professional SMM & Mobilografiya\n\nBo'limni tanlang:",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )
    return MAIN_MENU

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            MAIN_MENU: [
                CallbackQueryHandler(portfolio, pattern="^portfolio$"),
                CallbackQueryHandler(narx, pattern="^narx$"),
                CallbackQueryHandler(shartnoma_start, pattern="^shartnoma$"),
                CallbackQueryHandler(boglanish, pattern="^boglanish$"),
                CallbackQueryHandler(buyurtma, pattern="^buyurtma$"),
                CallbackQueryHandler(back_main, pattern="^back_main$"),
                CallbackQueryHandler(confirm_order, pattern="^confirm_(yes|no)_"),
            ],
            ORDER_VIDEO_COUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, order_video_count)],
            ORDER_WAIT_PRICE: [
                CallbackQueryHandler(confirm_order, pattern="^confirm_(yes|no)_"),
                CallbackQueryHandler(shartnoma_start, pattern="^shartnoma$"),
            ],
            CONTRACT_ISM: [MessageHandler(filters.TEXT & ~filters.COMMAND, contract_ism)],
            CONTRACT_FAMILYA: [MessageHandler(filters.TEXT & ~filters.COMMAND, contract_familya)],
            CONTRACT_PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, contract_phone)],
            CONTRACT_XIZMAT: [CallbackQueryHandler(contract_xizmat, pattern="^xizmat_")],
            CONTRACT_SUMMA: [MessageHandler(filters.TEXT & ~filters.COMMAND, contract_summa)],
            CONTRACT_MUDDAT: [CallbackQueryHandler(contract_muddat, pattern="^muddat_")],
            CONTRACT_CONFIRM: [
                CallbackQueryHandler(contract_confirm, pattern="^contract_confirm$"),
                CallbackQueryHandler(back_main, pattern="^back_main$"),
            ],
        },
        fallbacks=[CommandHandler("start", start)],
        allow_reentry=True,
    )
    app.add_handler(conv_handler)
    app.add_handler(CommandHandler("narx", admin_narx))
    print("✅ Pro Media Bot ishga tushdi!")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
