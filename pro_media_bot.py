import logging
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

# ===================== SOZLAMALAR =====================
BOT_TOKEN = "8708467547:AAE427mHcyo_tHO2CMwxc7PnEM1ErGWi4Fs"
ADMIN_ID = 8340818638

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Holatlar
(
    MAIN_MENU,
    ORDER_VIDEO_COUNT,
    ORDER_WAIT_PRICE,
    ORDER_CONFIRM,
    CONTRACT_ISM,
    CONTRACT_FAMILYA,
    CONTRACT_PHONE,
    CONTRACT_XIZMAT,
    CONTRACT_SUMMA,
    CONTRACT_MUDDAT,
    CONTRACT_CONFIRM,
) = range(11)

user_data_store = {}

# ===================== START =====================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    keyboard = [
        [InlineKeyboardButton("📁 Portfolio ko'rish", callback_data="portfolio")],
        [InlineKeyboardButton("💰 Narx-navo", callback_data="narx")],
        [InlineKeyboardButton("📄 Shartnoma tuzish", callback_data="shartnoma")],
        [InlineKeyboardButton("📞 Bog'lanish", callback_data="boglanish")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        f"👋 Salom, {user.first_name}!\n\n"
        "🎬 *Pro Media* — Professional SMM & Mobilografiya xizmatlari\n\n"
        "Quyidagi bo'limlardan birini tanlang:",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )
    return MAIN_MENU

# ===================== PORTFOLIO =====================
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
        "• Kontent rejasi\n\n"
        "_Portfoliomizni ko'rish uchun yuqoridagi havolalarga o'ting!_",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )

# ===================== NARX-NAVO =====================
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
        "┌─────────────────────────┐\n"
        "│ 10-12 ta video → $250-300 │\n"
        "│ 13-15 ta video → $300-350 │\n"
        "│ 16-20 ta video → $350-450 │\n"
        "└─────────────────────────┘\n\n"
        "📌 *1 ta video narxi:* $20 (mobil syomka + montaj)\n\n"
        "⏳ Shartnoma muddatlari:\n"
        "• 3 oylik\n"
        "• 6 oylik\n"
        "• 12 oylik (1 yil)\n\n"
        "_Aniq narx uchun xizmat buyurtma qiling!_",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )

# ===================== BUYURTMA =====================
async def buyurtma(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    user_data_store[user_id] = {"step": "video_count"}
    await query.edit_message_text(
        "🛒 *Xizmat buyurtma qilish*\n\n"
        "📹 Har oyda nechta video kerak?\n\n"
        "_Masalan: 12_",
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
        "user_username": update.effective_user.username or "yo'q",
        "user_id": user_id,
    }

    # Adminga xabar yuborish
    await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=f"🔔 *Yangi buyurtma!*\n\n"
             f"👤 Mijoz: {update.effective_user.full_name}\n"
             f"🆔 Username: @{update.effective_user.username or 'yoq'}\n"
             f"🆔 ID: `{user_id}`\n"
             f"📹 So'ralgan video soni: *{video_count} ta/oy*\n\n"
             f"💬 Narx tasdiqlash uchun:\n"
             f"`/narx_{user_id}_SUMMA`\n"
             f"_Masalan: /narx_{user_id}_300_",
        parse_mode="Markdown"
    )

    await update.message.reply_text(
        f"✅ *So'rovingiz qabul qilindi!*\n\n"
        f"📹 Video soni: *{video_count} ta/oy*\n\n"
        f"⏳ Administrator narxni tasdiqlaydi va sizga javob yuboradi.\n"
        f"Biroz kuting...",
        parse_mode="Markdown"
    )
    return ORDER_WAIT_PRICE

# ===================== ADMIN NARX YUBORISH =====================
async def admin_narx(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    try:
        parts = update.message.text.split("_")
        target_user_id = int(parts[1])
        summa = parts[2]

        user_data_store[target_user_id]["taklif_narx"] = summa

        keyboard = [
            [
                InlineKeyboardButton("✅ Roziman", callback_data=f"confirm_yes_{target_user_id}"),
                InlineKeyboardButton("❌ Rad etaman", callback_data=f"confirm_no_{target_user_id}"),
            ]
        ]

        await context.bot.send_message(
            chat_id=target_user_id,
            text=f"💰 *Narx taklifi keldi!*\n\n"
                 f"📹 Video soni: *{user_data_store[target_user_id].get('video_count', '?')} ta/oy*\n"
                 f"💵 Taklif narx: *${summa}/oy*\n\n"
                 f"Qabul qilasizmi?",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )
        await update.message.reply_text(f"✅ Narx ${summa} mijozga yuborildi!")
    except Exception as e:
        await update.message.reply_text(f"❌ Xato: {e}\nFormat: /narx_ID_SUMMA")

# ===================== MIJOZ TASDIQLASH =====================
async def confirm_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data.startswith("confirm_yes_"):
        target_id = int(data.split("_")[2])
        narx = user_data_store.get(target_id, {}).get("taklif_narx", "?")
        video_count = user_data_store.get(target_id, {}).get("video_count", "?")

        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=f"✅ *Mijoz narxni qabul qildi!*\n"
                 f"👤 ID: `{target_id}`\n"
                 f"💵 Narx: ${narx}/oy\n"
                 f"📹 Video: {video_count} ta/oy"
        )

        keyboard = [[InlineKeyboardButton("📄 Shartnoma tuzish", callback_data="shartnoma")]]
        await query.edit_message_text(
            f"✅ *Ajoyib! Kelishildi!*\n\n"
            f"💵 Narx: *${narx}/oy*\n\n"
            f"Endi shartnoma tuzamiz. Quyidagi tugmani bosing:",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )

    elif data.startswith("confirm_no_"):
        target_id = int(data.split("_")[2])
        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=f"❌ Mijoz ({target_id}) narxni rad etdi."
        )
        await query.edit_message_text(
            "❌ Tushunildi. Boshqa narx haqida muzokarа qilish uchun:\n📞 Bog'laning!"
        )

# ===================== SHARTNOMA =====================
async def shartnoma_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.callback_query:
        query = update.callback_query
        await query.answer()
        user_id = query.from_user.id
        await query.edit_message_text(
            "📄 *Shartnoma tuzish*\n\n"
            "Bosqichma-bosqich ma'lumot kiritamiz.\n\n"
            "👤 Ismingizni kiriting:\n_(Masalan: Jasur)_",
            parse_mode="Markdown"
        )
    else:
        user_id = update.effective_user.id
        await update.message.reply_text(
            "📄 *Shartnoma tuzish*\n\n"
            "👤 Ismingizni kiriting:\n_(Masalan: Jasur)_",
            parse_mode="Markdown"
        )

    user_data_store[user_id] = user_data_store.get(user_id, {})
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
        [InlineKeyboardButton("🎬 SMM + Video (oylik)", callback_data="xizmat_smm_video")],
        [InlineKeyboardButton("📱 Faqat Video (oylik)", callback_data="xizmat_video")],
        [InlineKeyboardButton("📊 SMM Boshqaruv (oylik)", callback_data="xizmat_smm")],
    ]
    await update.message.reply_text(
        "💼 Xizmat turini tanlang:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return CONTRACT_XIZMAT

async def contract_xizmat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    xizmat_map = {
        "xizmat_smm_video": "SMM + Mobil Videografiya (oylik kontent)",
        "xizmat_video": "Mobil Videografiya (oylik video ishlab chiqarish)",
        "xizmat_smm": "SMM Boshqaruv (ijtimoiy tarmoqlar)",
    }
    user_data_store[user_id]["contract"]["xizmat"] = xizmat_map[query.data]

    await query.edit_message_text(
        "💵 Kelishilgan summani kiriting ($ da):\n_(Masalan: 300)_",
        parse_mode="Markdown"
    )
    return CONTRACT_SUMMA

async def contract_summa(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text.strip().replace("$", "").replace(" ", "")

    if not text.replace(".", "").isdigit():
        await update.message.reply_text("❌ Iltimos, faqat raqam kiriting. Masalan: 300")
        return CONTRACT_SUMMA

    user_data_store[user_id]["contract"]["summa"] = text

    keyboard = [
        [InlineKeyboardButton("📅 3 oylik", callback_data="muddat_3")],
        [InlineKeyboardButton("📅 6 oylik", callback_data="muddat_6")],
        [InlineKeyboardButton("📅 12 oylik (1 yil)", callback_data="muddat_12")],
    ]
    await update.message.reply_text(
        "⏳ Shartnoma muddatini tanlang:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return CONTRACT_MUDDAT

async def contract_muddat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    muddat_map = {"muddat_3": "3 oy", "muddat_6": "6 oy", "muddat_12": "12 oy (1 yil)"}
    user_data_store[user_id]["contract"]["muddat"] = muddat_map[query.data]

    c = user_data_store[user_id]["contract"]
    oylik = float(c["summa"])
    muddat_raqam = int(query.data.split("_")[1])
    jami = oylik * muddat_raqam
    oldindan = oylik  # 1 oylik oldindan to'lov

    user_data_store[user_id]["contract"]["jami"] = str(jami)
    user_data_store[user_id]["contract"]["oldindan"] = str(oldindan)

    keyboard = [
        [
            InlineKeyboardButton("✅ Tasdiqlash", callback_data="contract_confirm"),
            InlineKeyboardButton("❌ Bekor qilish", callback_data="back_main"),
        ]
    ]

    await query.edit_message_text(
        f"📄 *Shartnoma ma'lumotlari:*\n\n"
        f"👤 Ism: *{c['ism']} {c['familya']}*\n"
        f"📞 Tel: *{c['phone']}*\n"
        f"💼 Xizmat: *{c['xizmat']}*\n"
        f"💵 Oylik narx: *${c['summa']}*\n"
        f"⏳ Muddat: *{c['muddat']}*\n"
        f"💰 Jami summa: *${jami}*\n"
        f"🔐 Oldindan to'lov: *${oldindan}*\n\n"
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

    # Mijozga yuborish
    with open(pdf_path, "rb") as f:
        await context.bot.send_document(
            chat_id=user_id,
            document=f,
            filename=f"Shartnoma_{c['ism']}_{c['familya']}.pdf",
            caption=f"✅ *Shartnomangiz tayyor!*\n\n"
                    f"🖨️ Chop etib, imzo qo'ying.\n"
                    f"💵 Oldindan to'lov: *${c['oldindan']}*\n\n"
                    f"To'lovdan so'ng ish boshlanadi! 🚀",
            parse_mode="Markdown"
        )

    # Adminga yuborish
    with open(pdf_path, "rb") as f:
        await context.bot.send_document(
            chat_id=ADMIN_ID,
            document=f,
            filename=f"Shartnoma_{c['ism']}_{c['familya']}.pdf",
            caption=f"📄 *Yangi shartnoma!*\n\n"
                    f"👤 {c['ism']} {c['familya']}\n"
                    f"📞 {c['phone']}\n"
                    f"💵 ${c['summa']}/oy | {c['muddat']}\n"
                    f"💰 Jami: ${c['jami']}\n"
                    f"🔐 Oldindan: ${c['oldindan']}",
            parse_mode="Markdown"
        )

    os.remove(pdf_path)
    return MAIN_MENU

# ===================== PDF GENERATOR =====================
def generate_contract_pdf(c, user_id):
    filename = f"contract_{user_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf"
    doc = SimpleDocTemplate(
        filename,
        pagesize=A4,
        rightMargin=2*cm,
        leftMargin=2*cm,
        topMargin=2*cm,
        bottomMargin=2*cm
    )

    styles = getSampleStyleSheet()
    story = []

    title_style = ParagraphStyle(
        'title', parent=styles['Normal'],
        fontSize=16, fontName='Helvetica-Bold',
        alignment=TA_CENTER, spaceAfter=6
    )
    subtitle_style = ParagraphStyle(
        'subtitle', parent=styles['Normal'],
        fontSize=10, fontName='Helvetica',
        alignment=TA_CENTER, spaceAfter=2, textColor=colors.grey
    )
    heading_style = ParagraphStyle(
        'heading', parent=styles['Normal'],
        fontSize=11, fontName='Helvetica-Bold',
        spaceBefore=12, spaceAfter=4
    )
    normal_style = ParagraphStyle(
        'normal', parent=styles['Normal'],
        fontSize=10, fontName='Helvetica',
        spaceAfter=4, leading=16
    )

    today = datetime.now()
    date_str = today.strftime("%d.%m.%Y")

    # Header
    story.append(Paragraph("XIZMAT KO'RSATISH SHARTNOMASI", title_style))
    story.append(Paragraph("SERVICE AGREEMENT CONTRACT", subtitle_style))
    story.append(Spacer(1, 0.3*cm))
    story.append(HRFlowable(width="100%", thickness=2, color=colors.black))
    story.append(Spacer(1, 0.3*cm))

    # Info table
    info_data = [
        ["Sana / Date:", date_str, "Shartnoma №:", f"PM-{today.strftime('%Y%m%d')}-{user_id % 1000:03d}"],
    ]
    info_table = Table(info_data, colWidths=[3.5*cm, 6*cm, 3.5*cm, 4*cm])
    info_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTNAME', (0, 0), (0, 0), 'Helvetica-Bold'),
        ('FONTNAME', (2, 0), (2, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(info_table)
    story.append(Spacer(1, 0.5*cm))

    # Tomonlar
    story.append(Paragraph("TOMONLAR / PARTIES", heading_style))
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.grey))
    story.append(Spacer(1, 0.2*cm))

    parties_data = [
        ["IJROCHI / EXECUTOR:", "Pro Media", "BUYURTMACHI / CLIENT:", f"{c['ism']} {c['familya']}"],
        ["Xizmat turi:", "SMM & Mobilografiya", "Telefon:", c['phone']],
        ["Telegram:", "@ProMediaAdmin_bot", "Imzo:", "_______________"],
    ]
    parties_table = Table(parties_data, colWidths=[4*cm, 5.5*cm, 4*cm, 5.5*cm])
    parties_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTNAME', (0, 0), (0, 0), 'Helvetica-Bold'),
        ('FONTNAME', (2, 0), (2, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9.5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BACKGROUND', (0, 0), (0, 0), colors.lightgrey),
        ('BACKGROUND', (2, 0), (2, 0), colors.lightgrey),
    ]))
    story.append(parties_table)
    story.append(Spacer(1, 0.5*cm))

    # Shartnoma tafsilotlari
    story.append(Paragraph("SHARTNOMA TAFSILOTLARI / CONTRACT DETAILS", heading_style))
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.grey))
    story.append(Spacer(1, 0.2*cm))

    muddat_raqam = int(c['muddat'].split()[0])
    details_data = [
        ["Ko'rsatiladigan xizmat:", c['xizmat']],
        ["Shartnoma muddati:", c['muddat']],
        ["Boshlash sanasi:", date_str],
        ["Tugash sanasi:", datetime(today.year, today.month + muddat_raqam if today.month + muddat_raqam <= 12 else (today.month + muddat_raqam) % 12, today.day).strftime("%d.%m.%Y") if today.month + muddat_raqam <= 12 else f"+{muddat_raqam} oy"],
    ]
    details_table = Table(details_data, colWidths=[5*cm, 12*cm])
    details_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('ROWBACKGROUNDS', (0, 0), (-1, -1), [colors.white, colors.Color(0.96, 0.96, 0.96)]),
    ]))
    story.append(details_table)
    story.append(Spacer(1, 0.5*cm))

    # To'lov
    story.append(Paragraph("TO'LOV SHARTLARI / PAYMENT TERMS", heading_style))
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.grey))
    story.append(Spacer(1, 0.2*cm))

    payment_data = [
        ["TO'LOV TURI", "SUMMA ($)", "IZOH"],
        ["Oylik to'lov", f"${c['summa']}", "Har oy boshida"],
        ["Jami shartnoma summasi", f"${c['jami']}", f"{c['muddat']} uchun"],
        ["OLDINDAN TO'LOV", f"${c['oldindan']}", "Ish boshlanishidan oldin"],
    ]
    payment_table = Table(payment_data, colWidths=[6*cm, 4*cm, 7*cm])
    payment_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.black),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('BACKGROUND', (0, -1), (-1, -1), colors.Color(0.9, 0.95, 0.9)),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('ALIGN', (1, 0), (1, -1), TA_CENTER),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 7),
        ('TOPPADDING', (0, 0), (-1, -1), 7),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -2), [colors.white, colors.Color(0.96, 0.96, 0.96)]),
    ]))
    story.append(payment_table)
    story.append(Spacer(1, 0.5*cm))

    # Shartlar
    story.append(Paragraph("ASOSIY SHARTLAR / MAIN CONDITIONS", heading_style))
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.grey))
    story.append(Spacer(1, 0.2*cm))

    conditions = [
        "1. Ijrochi buyurtmachi bilan kelishilgan hajmda sifatli kontent tayyorlashni o'z zimmasiga oladi.",
        "2. Buyurtmachi har oy belgilangan miqdorda to'lov amalga oshirishga majburdir.",
        "3. Oldindan to'lov amalga oshirilgandan keyin ish boshlash kafolatlanadi.",
        "4. Shartnomani bekor qilish uchun 15 kun oldin xabar berish shart.",
        "5. Kontent huquqlari shartnoma muddati davomida buyurtmachiga tegishli.",
        "6. Ixtilof holatlari muzokaralar orqali hal etiladi.",
    ]
    for cond in conditions:
        story.append(Paragraph(cond, normal_style))

    story.append(Spacer(1, 0.8*cm))

    # Imzo
    story.append(HRFlowable(width="100%", thickness=1, color=colors.black))
    story.append(Spacer(1, 0.3*cm))

    sign_data = [
        ["IJROCHI / EXECUTOR", "", "BUYURTMACHI / CLIENT"],
        ["Pro Media", "", f"{c['ism']} {c['familya']}"],
        ["", "", ""],
        ["Imzo: _______________", "", "Imzo: _______________"],
        [date_str, "", date_str],
    ]
    sign_table = Table(sign_data, colWidths=[7*cm, 3*cm, 7*cm])
    sign_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTNAME', (0, 0), (0, 0), 'Helvetica-Bold'),
        ('FONTNAME', (2, 0), (2, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('ALIGN', (0, 0), (0, -1), TA_LEFT),
        ('ALIGN', (2, 0), (2, -1), TA_RIGHT),
    ]))
    story.append(sign_table)

    doc.build(story)
    return filename

# ===================== BOG'LANISH =====================
async def boglanish(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    keyboard = [[InlineKeyboardButton("🔙 Orqaga", callback_data="back_main")]]
    await query.edit_message_text(
        "📞 *Bog'lanish*\n\n"
        "👤 Admin: @ProMediaAdmin\n"
        "📱 Telefon: +998 XX XXX XX XX\n"
        "📸 Instagram: @pro_media_uz\n\n"
        "_Ish vaqti: 09:00 - 22:00_",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )

# ===================== ORQAGA =====================
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
        "🏠 *Asosiy menyu*\n\n"
        "🎬 *Pro Media* — Professional SMM & Mobilografiya\n\n"
        "Bo'limni tanlang:",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )
    return MAIN_MENU

# ===================== MAIN =====================
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
            ORDER_VIDEO_COUNT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, order_video_count)
            ],
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
    app.run_polling()

if __name__ == "__main__":
    main()
