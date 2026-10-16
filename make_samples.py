#!/usr/bin/env python3
"""Builds the sample files used in the video. You don't need this to use pdfchat.py.

    pip3 install reportlab pymupdf pillow
    python3 make_samples.py

Writes:
  sample.pdf          a 30-page FICTIONAL rental agreement (Harbor Lane Properties). No real company or person.
  sample-scanned.pdf  the same lease as page photos only (no text layer), to show the "No text found" stop
  move-in-guide.pdf   a 3-page guide for the quick drag-and-drop demo
"""
import io, random
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
from reportlab.pdfgen import canvas

LANDLORD = "Dana Whitcombe"          # appears on page 1 only
TENANT = "Jordan Reyes"
MANAGER = "Marcus Bell"              # the property manager, mid-document (a plausible wrong answer)
ADDRESS = "Unit 4B, 18 Harbor Lane, Port Alder"

ss = getSampleStyleSheet()
BODY = ParagraphStyle("body", parent=ss["BodyText"], fontName="Times-Roman", fontSize=12, leading=17, spaceAfter=9)
H1 = ParagraphStyle("h1", parent=ss["Heading1"], fontName="Helvetica-Bold", fontSize=15, spaceAfter=12)
TITLE = ParagraphStyle("title", parent=ss["Title"], fontName="Helvetica-Bold", fontSize=20, spaceAfter=6)


class Numbered(canvas.Canvas):
    """'Page N of M' footer and a running header."""
    def __init__(self, *a, header="HARBOR LANE PROPERTIES  ·  Residential Lease", **k):
        super().__init__(*a, **k)
        self._pages, self._header = [], header

    def showPage(self):
        self._pages.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        n = len(self._pages)
        for st in self._pages:
            self.__dict__.update(st)
            self.setFont("Helvetica", 9)
            self.setFillColor(colors.grey)
            self.drawString(inch, letter[1] - 0.6 * inch, self._header)
            self.drawCentredString(letter[0] / 2, 0.55 * inch, f"Page {self._pageNumber} of {n}")
            super().showPage()
        super().save()

# Extra clause text per section (keeps one section per page, and makes the lease long enough to overflow a 4K window).
EXTRA = {
 "2. TERM": [
  "The Tenant may ask to move in up to three (3) days before the Start Date if the Premises are ready. Rent for those days "
  "is charged per day as set out in section 3.",
  "If either party wants to change the Start Date, the change must be agreed in writing before the keys are collected. "
  "A verbal agreement is not enough to change the term of this Lease."],
 "3. RENT": [
  "The Landlord will send a rent statement by email at the start of each quarter, showing payments received and any "
  "charges added. The Tenant should check each statement and raise any error within thirty (30) days.",
  "Cash payments are not accepted at the site office. If the Tenant pays more than the rent due, the extra amount is "
  "kept as a credit and set against the next month's rent, unless the Tenant asks for it to be refunded.",
  "Rent is not reduced because the Tenant is away from the Premises, or because a service paid for by the Tenant, "
  "such as internet, is interrupted."],
 "4. LATE PAYMENT AND RETURNED PAYMENTS": [
  "If the Tenant expects to pay late, the Tenant should tell the property manager before the due date. A payment plan "
  "agreed in writing before the fifth day of the month means the late fee is not charged for that month.",
  "Rent that is more than thirty (30) days overdue may be referred to a collection agency, and the Landlord may treat "
  "two months of unpaid rent as a serious breach of this Lease."],
 "5. SECURITY DEPOSIT": [
  "Within thirty (30) days of receiving the deposit, the Landlord will give the Tenant written details of the account "
  "or scheme in which it is held, and how to contact that scheme.",
  "If the deposit is used during the tenancy to cover unpaid rent or damage, the Tenant must top it back up to the full "
  "amount within fourteen (14) days of being asked in writing."],
 "7. UTILITIES AND SERVICES": [
  "Meter readings are taken on the Start Date and on the last day of the tenancy and recorded in Schedule A. The Tenant "
  "pays for all electricity used between those two readings.",
  "If the Tenant leaves an account unpaid and the supplier charges the Landlord, the amount may be deducted from the "
  "deposit, with a copy of the bill provided to the Tenant.",
  "The building has a shared fibre connection. The Tenant may choose any provider that offers service on that connection, "
  "but must not install a satellite dish or external aerial."],
 "8. USE OF THE PREMISES": [
  "The Tenant must not keep anything in the Premises that is dangerous or likely to cause a fire, such as fuel cans or "
  "gas bottles, and must not use portable heaters that burn fuel.",
  "Window restrictors are fitted for safety and must not be removed. Balcony doors must be kept closed when the "
  "Premises are empty, and nothing may be thrown or shaken from the balcony.",
  "The Tenant must allow the yearly gas safety check and the electrical safety inspection to take place on the dates "
  "the Landlord arranges, after notice under section 13."],
 "9. OCCUPANTS AND GUESTS": [
  "If the occupant named above moves out, the Tenant should tell the Landlord in writing. A new adult occupant can be "
  "added only after the Landlord has completed the usual reference checks.",
  "Guests must follow the house rules in Schedule B, including the rules on smoking and noise. The Tenant must not give "
  "building fobs or keys to guests who are not staying at the Premises."],
 "10. PETS": [
  "An approved pet must be kept under control in the shared areas of the building, and dogs must be on a lead in the "
  "hallways and the lift.",
  "The Tenant is responsible for any damage, smell or flea treatment caused by a pet, and for cleaning up after the pet "
  "in the shared areas and the grounds.",
  "Consent for a pet can be withdrawn if the pet causes repeated complaints from neighbours that are confirmed by the "
  "property manager."],
 "11. MAINTENANCE AND REPAIRS": [
  "When reporting a repair, the Tenant should give a short description, the room, and a photo where possible. Each "
  "report receives a reference number by email.",
  "Contractors sent by the property manager carry photo identification. The Tenant may ask to see it before letting "
  "anyone into the Premises."],
 "12. EMERGENCY REPAIRS": [
  "If water is leaking, the Tenant should turn off the main stopcock, which is in the kitchen under the sink. If there "
  "is a smell of gas, the Tenant should open the windows, leave the Premises, and call the gas emergency number first.",
  "The Tenant must not attempt electrical or gas repairs. Only qualified contractors arranged through the emergency "
  "line may work on the boiler, the wiring or the gas supply."],
 "13. LANDLORD'S ENTRY": [
  "Routine inspections take place no more than once every three (3) months. The Tenant will receive a short written "
  "report after each inspection, listing anything that needs attention.",
  "During the last sixty (60) days of the tenancy, the Landlord may show the Premises to possible new tenants up to "
  "twice a week, after giving notice as above.",
  "If the Tenant will be away for more than fourteen (14) days in a row, the Tenant should tell the property manager, "
  "so that the Premises can be checked in an emergency."],
 "14. ALTERATIONS AND DECORATION": [
  "With consent, the Tenant may paint rooms in a neutral colour, provided the work is done to a good standard. The "
  "Landlord may ask for the original colour to be restored at the end of the tenancy.",
  "The Tenant may fit a doorbell camera or smart lock only with written consent, and must remove it and make good any "
  "holes when moving out.",
  "Any fixture the Tenant adds with consent becomes part of the Premises if it cannot be removed without damage, unless "
  "the Landlord and the Tenant agree otherwise in writing."],
 "15. APPLIANCES": [
  "Manuals for each appliance are kept in the kitchen drawer next to the oven. Filters in the dishwasher and the "
  "washer-dryer should be cleaned once a month.",
  "If the Tenant brings additional large appliances, such as a second freezer, the Tenant must tell the property manager "
  "first, so that the electrical load can be checked.",
  "Damage caused by misuse, such as overloading the washer-dryer or leaving items in the oven, may be charged to the "
  "Tenant at the cost of the repair."],
 "16. SMOKE AND CARBON MONOXIDE ALARMS": [
  "If an alarm sounds without a reason, or beeps to show a low battery, the Tenant should test it and report any fault "
  "on the repairs line the same day.",
  "The Landlord will test every alarm at the start of the tenancy and record the result in Schedule A, and will replace "
  "any alarm that is more than ten years old."],
 "17. NOISE AND QUIET HOURS": [
  "Parties or gatherings of more than ten people need the property manager's agreement in advance and must end by the "
  "start of quiet hours.",
  "Building work by the Tenant, such as drilling to hang shelves, is allowed only between 9 a.m. and 6 p.m. on weekdays "
  "and between 10 a.m. and 4 p.m. on Saturdays.",
  "If a neighbour's noise is a problem, the Tenant can report it to the property manager, who will deal with it under "
  "the same rules."],
 "18. WASTE AND RECYCLING": [
  "Glass, cans, paper and card go in the blue recycling bins. Food waste goes in the brown caddy, which is emptied on "
  "Fridays. General waste goes in the black bins.",
  "Large items such as furniture or mattresses can be collected by arrangement with the property manager. The cost of "
  "removing items left in the bin store may be charged to the Tenant who left them."],
 "19. INSURANCE": [
  "Contents insurance is not a condition of this Lease, but without it the Tenant's belongings are not covered for "
  "fire, flood or theft.",
  "If the Tenant causes damage to the building, for example by leaving a tap running, the Landlord's insurer may claim "
  "the cost back from the Tenant. Contents insurance with tenant's liability cover protects against this.",
  "The Tenant must tell the Landlord promptly about any event that could lead to an insurance claim on the building."],
 "20. SUBLETTING AND ASSIGNMENT": [
  "If the Tenant needs to leave during the fixed term, the Tenant may ask the Landlord to accept a replacement tenant. "
  "The Landlord will not unreasonably refuse a replacement who passes the usual reference checks.",
  "Where a replacement tenant is accepted, the Tenant pays a reasonable administration charge, agreed in advance, and "
  "remains responsible for rent until the new lease starts.",
  "Any money received for letting the Premises without consent must be paid to the Landlord."],
 "21. RENEWAL": [
  "A renewal may be for a further fixed term of six (6) or twelve (12) months. The deposit carries over to the new "
  "lease, and a new inventory check is not needed unless either party asks for one.",
  "If no new lease is agreed by the end of the term, section 2 applies and the tenancy continues from month to month."],
 "22. RENT CHANGES": [
  "A rent increase may take place no more than once in any twelve (12) month period, and the notice will show the new "
  "amount and the date from which it applies.",
  "If the Tenant does not accept the new rent, the Tenant may end the tenancy by giving notice under section 23 before "
  "the increase takes effect."],
 "24. MOVING OUT": [
  "The Tenant should arrange for utilities and internet accounts to be closed or moved on the last day, and give a "
  "forwarding address in writing.",
  "Items left in the Premises after the tenancy ends will be stored for fourteen (14) days. If they are not collected "
  "in that time, they may be disposed of, and the reasonable cost charged to the Tenant.",
  "The Tenant may ask for a pre-move-out visit during the notice period, so that any likely deductions can be "
  "discussed in advance."],
 "25. RETURN OF DEPOSIT": [
  "The deposit is returned to the bank account from which it was paid, unless the Tenant asks in writing for a "
  "different account.",
  "If the Tenant disagrees with a deduction, the Tenant should say so in writing within fourteen (14) days. The part of "
  "the deposit that is not in dispute will be returned while the disagreement is resolved."],
 "26. DISPUTES": [
  "For other disputes, the parties may agree to use a mediation service before going to court. Each party pays its own "
  "costs of mediation unless they agree otherwise.",
  "This Lease is governed by the law of the place where the Premises are located. If any part of it is found to be "
  "unenforceable, the rest of the Lease remains in effect."],
 "27. NOTICES": [
  "A notice sent by email is treated as received on the next working day after it is sent. A notice sent by post is "
  "treated as received two (2) working days after posting.",
  "Each party must tell the other promptly if their address for notices or email address changes."],
}


def P(t):
    return Paragraph(t, BODY)


def section(story, title, paras, new_page=True):
    if new_page:
        story.append(PageBreak())
    story.append(Paragraph(title, H1))
    for p in list(paras) + EXTRA.get(title, []):
        story.append(P(p) if isinstance(p, str) else p)


def table(rows, widths, head=True):
    t = Table(rows, colWidths=widths)
    st = [("FONT", (0, 0), (-1, -1), "Times-Roman", 11), ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
          ("VALIGN", (0, 0), (-1, -1), "TOP"), ("BOTTOMPADDING", (0, 0), (-1, -1), 5)]
    if head:
        st += [("FONT", (0, 0), (-1, 0), "Helvetica-Bold", 11), ("BACKGROUND", (0, 0), (-1, 0), colors.whitesmoke)]
    t.setStyle(TableStyle(st))
    return t


def lease_story():
    s = [Paragraph("Residential Lease Agreement", TITLE), Paragraph("Harbor Lane Properties", H1), Spacer(1, 6)]
    section(s, "1. PARTIES AND PROPERTY", [
        f"This Residential Lease Agreement (the \"Lease\") is made on 1 September 2026 between {LANDLORD} (the \"Landlord\") "
        f"and {TENANT} (the \"Tenant\"). Harbor Lane Properties is the trading name under which the Landlord lets this home.",
        f"The Landlord agrees to let, and the Tenant agrees to rent, the apartment known as {ADDRESS} (the \"Premises\"), "
        "together with the fixtures, fittings and furniture listed in Schedule A.",
        "The Premises are let as a private residence for the Tenant and the occupants named in section 9 only. "
        "The Tenant has inspected the Premises before signing and accepts them in the condition recorded in Schedule A.",
        "In this Lease, \"days\" means calendar days unless stated otherwise, and \"written notice\" means a letter "
        "or an email sent to the address for notices in section 27.",
    ], new_page=False)
    section(s, "2. TERM", [
        "The Lease begins on 1 September 2026 (the \"Start Date\") and continues for a fixed term of twelve (12) months, "
        "ending on 31 August 2027, unless it is renewed under section 21 or ended earlier under section 23.",
        "The Tenant may collect the keys on the Start Date. If the Premises are not ready on the Start Date for reasons "
        "outside the Tenant's control, rent will not be charged for the days the Tenant cannot move in.",
        "If the Tenant stays in the Premises after the end of the term without a renewal, the Lease continues from month "
        "to month on the same terms until either party ends it under section 23.",
    ])
    section(s, "3. RENT", [
        "The rent is $1,850 (one thousand eight hundred and fifty dollars) per month, payable in advance on or before "
        "the first (1st) day of each month.",
        "Rent is paid by bank transfer to the account shown on the rent statement. The Tenant should use the unit number, "
        "4B, as the payment reference so that the payment can be matched to this Lease.",
        "The first month's rent is due on signing, together with the security deposit described in section 5.",
        "If the term starts or ends part of the way through a month, the rent for that month is charged per day, "
        "at one thirtieth (1/30) of the monthly rent for each day.",
    ])
    section(s, "4. LATE PAYMENT AND RETURNED PAYMENTS", [
        "If the full rent has not been received by the end of the fifth (5th) day of the month, a late fee of $75 is "
        "added to the Tenant's account. The late fee is charged once per month and is not a daily charge.",
        "If a payment is returned or reversed by the Tenant's bank, a returned payment fee of $35 applies, and the rent "
        "is treated as unpaid until a replacement payment clears.",
        "Late fees are listed with the other charges in the fee table in section 6. Paying a late fee does not change the "
        "date on which rent is due.",
    ])
    section(s, "5. SECURITY DEPOSIT", [
        "On signing, the Tenant pays a security deposit of $1,850, equal to one month's rent. The deposit is held in a "
        "separate account and does not earn interest for the Tenant.",
        "The deposit is security for unpaid rent, damage beyond normal wear and tear, and any cleaning needed to return "
        "the Premises to the condition recorded in Schedule A.",
        "The deposit cannot be used by the Tenant as the last month's rent. How and when the deposit is returned is set "
        "out in section 25.",
    ])
    section(s, "6. FEES", [
        "The following charges may apply during the Lease. No other fees are charged unless both parties agree in writing.",
        table([["Item", "Amount", "When it applies"],
               ["Late rent", "$75", "Rent not received by the end of the 5th day of the month"],
               ["Returned payment", "$35", "A payment is returned or reversed by the bank"],
               ["Replacement key", "$25", "Each extra or lost key"],
               ["Replacement fob", "$40", "Each extra or lost building entry fob"],
               ["Lock change", "$120", "Locks changed at the Tenant's request or after lost keys"],
               ["Pet fee", "$300", "One-off, if a pet is approved under section 10"],
               ["Professional cleaning", "Cost", "Only if the Premises are not left clean at the end"]],
              [1.7 * inch, 0.9 * inch, 3.6 * inch]),
        Spacer(1, 10),
        "All amounts are in US dollars and include any applicable tax.",
    ])
    section(s, "7. UTILITIES AND SERVICES", [
        "The Tenant pays for electricity, internet and any television services used at the Premises, and must open "
        "accounts in the Tenant's own name from the Start Date.",
        "Water, sewer and the heating of common areas are included in the rent. The Landlord pays the building insurance "
        "and the costs of maintaining the shared hallways and the lift.",
        "The Tenant must not change the supplier of any service that is billed to the building as a whole.",
    ])
    section(s, "8. USE OF THE PREMISES", [
        "The Tenant will use the Premises only as a private home. Running a business that brings customers or deliveries "
        "to the Premises is not allowed, although working from home is permitted.",
        "The Tenant must keep the Premises clean, ventilate them regularly to prevent damp, and report any sign of mould, "
        "leaks or pests promptly.",
        "Nothing may be stored in the shared hallways or on the stairs, which must be kept clear as fire escape routes.",
    ])
    section(s, "9. OCCUPANTS AND GUESTS", [
        "Only the Tenant and the following occupant may live at the Premises: Sam Reyes. Any other person staying for more "
        "than fourteen (14) nights in any three-month period needs the Landlord's written consent.",
        "The Tenant is responsible for the behaviour of guests, and for any damage they cause.",
    ])
    section(s, "10. PETS", [
        "No pets may be kept at the Premises without the Landlord's written consent, which will not be unreasonably refused "
        "for one cat or one small dog.",
        "If a pet is approved, the one-off pet fee in section 6 applies, and the Tenant must have the carpets professionally "
        "cleaned at the end of the Lease.",
        "Fish in a tank of under 40 litres do not need consent.",
    ])
    section(s, "11. MAINTENANCE AND REPAIRS", [
        f"Day-to-day repairs are handled by the property manager, {MANAGER}, who can be reached at "
        "repairs@harborlane.example or on the repairs line listed in Schedule B.",
        "The Landlord is responsible for keeping the structure, roof, windows, plumbing, heating and electrical systems in "
        "good repair, and for repairing appliances supplied with the Premises.",
        "The Tenant is responsible for replacing light bulbs and smoke alarm batteries, keeping drains clear, and repairing "
        "any damage caused by the Tenant, occupants or guests.",
        "Non-urgent repairs will normally be started within ten (10) working days of being reported.",
    ])
    section(s, "12. EMERGENCY REPAIRS", [
        "An emergency is a fault that puts people or the building at risk, such as a burst pipe, a gas smell, a total loss "
        "of heating in winter, or a door that cannot be locked.",
        "Emergencies should be reported immediately by phone on the emergency line in Schedule B, which is answered at all "
        "hours. The Landlord will arrange an emergency repair within twenty-four (24) hours.",
        "If the Tenant cannot reach anyone, the Tenant may arrange an urgent repair up to $250 and will be reimbursed on "
        "showing the receipt.",
    ])
    section(s, "13. LANDLORD'S ENTRY", [
        "The Landlord or the property manager may enter the Premises to inspect them, carry out repairs, or show them to "
        "future tenants or buyers, after giving at least twenty-four (24) hours' written notice.",
        "Visits will take place between 9 a.m. and 6 p.m. on weekdays unless the Tenant agrees otherwise. No notice is needed "
        "in an emergency.",
    ])
    section(s, "14. ALTERATIONS AND DECORATION", [
        "The Tenant must not make alterations, change the locks, or paint the Premises without written consent.",
        "Small picture hooks are allowed. Holes larger than a picture hook must be filled and repainted before the Tenant "
        "moves out.",
    ])
    section(s, "15. APPLIANCES", [
        "The Premises come with a fridge-freezer, an oven and hob, a dishwasher, and a washer-dryer, as listed in Schedule A.",
        "The Tenant must use the appliances in line with the manufacturer's instructions and report faults promptly. "
        "Repairs caused by normal use are the Landlord's responsibility.",
    ])
    section(s, "16. SMOKE AND CARBON MONOXIDE ALARMS", [
        "The Premises have a smoke alarm in the hallway and the living room and a carbon monoxide alarm next to the boiler.",
        "The Tenant must test the alarms once a month and replace batteries when needed, and must never disconnect an alarm.",
    ])
    section(s, "17. NOISE AND QUIET HOURS", [
        "Quiet hours in the building are from 10 p.m. to 7 a.m. every day. During quiet hours, music, televisions and "
        "appliances must be kept at a level that cannot be heard in neighbouring homes.",
        "Repeated noise complaints that are confirmed by the property manager may be treated as a breach of this Lease.",
    ])
    section(s, "18. WASTE AND RECYCLING", [
        "Household waste and recycling must be bagged and placed in the bins in the bin store on the ground floor. Bulky "
        "items must not be left in the bin store.",
        "Collections take place on Tuesdays and Fridays.",
    ])
    section(s, "19. INSURANCE", [
        "The Landlord insures the building. That insurance does not cover the Tenant's belongings, and the Tenant is advised "
        "to take out contents insurance from the Start Date.",
    ])
    section(s, "20. SUBLETTING AND ASSIGNMENT", [
        "The Tenant must not sublet the Premises, take in a lodger, or let them on a short-stay website, and must not "
        "transfer this Lease to anyone else without the Landlord's written consent.",
    ])
    section(s, "21. RENEWAL", [
        "At least ninety (90) days before the end of the term, the Landlord will tell the Tenant in writing whether a new "
        "lease is offered and on what terms.",
        "If the Tenant wants to renew, the Tenant should reply in writing within thirty (30) days of the offer.",
    ])
    section(s, "22. RENT CHANGES", [
        "The rent is fixed for the term of this Lease. Any change of rent for a renewal or a month-to-month tenancy will be "
        "given in writing at least sixty (60) days before it takes effect.",
    ])
    section(s, "23. TERMINATION", [
        "During the fixed term, the Lease can only be ended early by agreement, or as allowed by law.",
        "After the fixed term, or at its end, either party may end this lease by giving at least sixty (60) days' written "
        "notice. The notice must state the date on which the Tenant will move out, which must be the last day of a month.",
        "If the Tenant leaves before the end of the notice period, rent remains payable until the notice period ends, "
        "unless the Premises are let to a new tenant sooner.",
        "The Landlord may end the Lease early only for the reasons allowed by law, such as serious unpaid rent, and must give "
        "the notice the law requires.",
    ])
    section(s, "24. MOVING OUT", [
        "On the last day of the tenancy, the Tenant must return all keys and fobs, leave the Premises clean and empty, and "
        "take final meter readings.",
        "The Landlord and the Tenant will inspect the Premises together against Schedule A. Normal wear and tear is not "
        "charged.",
    ])
    section(s, "25. RETURN OF DEPOSIT", [
        "The deposit, less any lawful deductions, will be returned within twenty-one (21) days after the Tenant moves out "
        "and returns the keys.",
        "Any deduction will be explained in writing with an itemised list and copies of receipts or quotes.",
    ])
    section(s, "26. DISPUTES", [
        "If a dispute arises, the parties will first try to settle it by discussion. If that fails, either party may refer "
        "a dispute about the deposit to the deposit protection scheme's free dispute service.",
    ])
    section(s, "27. NOTICES", [
        "Notices to the Landlord must be sent to the address for notices: Harbor Lane Properties, 18 Harbor Lane, "
        "Port Alder, or by email to notices@harborlane.example.",
        "Notices to the Tenant may be delivered to the Premises or sent to the Tenant's email address on file.",
    ])
    section(s, "SCHEDULE A — INVENTORY", [
        table([["Room", "Item", "Condition at start"],
               ["Hallway", "Coat hooks (4), smoke alarm, entry phone", "Good"],
               ["Living room", "Sofa (3-seat, grey), coffee table, bookcase, curtains", "Good; small mark on sofa arm"],
               ["Living room", "Smoke alarm, two ceiling lights", "Good"],
               ["Kitchen", "Fridge-freezer, oven and hob, dishwasher", "Good; all tested"],
               ["Kitchen", "Washer-dryer, kettle, microwave", "Good"],
               ["Kitchen", "Table and four chairs", "Good; one chair slightly loose"],
               ["Bedroom 1", "Double bed and mattress, wardrobe, two bedside tables", "Good"],
               ["Bedroom 1", "Blinds, ceiling light", "Good"],
               ["Bedroom 2", "Single bed and mattress, desk, chair", "Good"],
               ["Bathroom", "Bath with shower, mirror cabinet, towel rail", "Good; grout clean"],
               ["Boiler cupboard", "Boiler, carbon monoxide alarm", "Serviced August 2026"],
               ["Keys", "Two front-door keys, two building fobs, one mailbox key", "All working"]],
              [1.4 * inch, 3.0 * inch, 1.8 * inch]),
    ])
    section(s, "SCHEDULE B — HOUSE RULES AND CONTACTS", [
        "Repairs line (working hours): 555-0142. Emergency line (all hours): 555-0199.",
        "Smoking and vaping are not allowed anywhere in the building, including balconies.",
        "Bicycles must be kept inside the Premises or in the ground-floor bike room, not in hallways.",
        "Barbecues are not allowed on balconies.",
        "Laundry must not be hung from windows or balconies.",
        "Lift problems should be reported on the repairs line.",
    ])
    section(s, "SIGNATURES", [
        "By signing below, the parties agree to the terms of this Lease, including Schedules A and B.",
        Spacer(1, 30), "Landlord signature: ______________________________   Date: ____________",
        Spacer(1, 30), "Tenant signature: ________________________________   Date: ____________",
        Spacer(1, 30), "Occupant signature: ______________________________   Date: ____________",
    ])
    return s


def guide_story():
    s = [Paragraph("Move-in Guide", TITLE), Paragraph("Harbor Lane Properties · Unit 4B", H1),
         P("Welcome to 18 Harbor Lane. This short guide covers your first day: keys, meters, bins and who to call."),
         P("Before you arrive, set up your electricity and internet accounts so they start on your move-in day.")]
    section(s, "Your keys", [
        "Keys can be collected from 10 a.m. on your move-in day at the Harbor Lane site office on the ground floor. "
        "Please bring photo ID.",
        "You will receive two front-door keys, two building fobs and one mailbox key.",
    ])
    section(s, "Meters, bins and contacts", [
        "Take a photo of the electricity meter when you arrive. Bins are collected on Tuesdays and Fridays.",
        "Repairs line: 555-0142. Emergency line (all hours): 555-0199.",
    ])
    return s


def build(path, story, header):
    doc = SimpleDocTemplate(path, pagesize=letter, leftMargin=inch, rightMargin=inch, topMargin=inch, bottomMargin=inch)
    doc.build(story, canvasmaker=lambda *a, **k: Numbered(*a, header=header, **k))


def scanned(src, dst):
    """Image-only copy: each page rendered, slightly rotated, with grain. No text layer."""
    import fitz
    from PIL import Image, ImageFilter
    rnd = random.Random(7)
    pages = []
    for page in fitz.open(src):
        pix = page.get_pixmap(dpi=150)
        im = Image.open(io.BytesIO(pix.tobytes("png"))).convert("L")
        im = im.rotate(rnd.uniform(-0.8, 0.8), resample=Image.BICUBIC, fillcolor=245)
        noise = Image.effect_noise(im.size, 18)
        im = Image.blend(im, noise, 0.06).filter(ImageFilter.GaussianBlur(0.4))
        pages.append(im.convert("RGB"))
    pages[0].save(dst, save_all=True, append_images=pages[1:], resolution=150)


if __name__ == "__main__":
    build("sample.pdf", lease_story(), "HARBOR LANE PROPERTIES  ·  Residential Lease")
    build("move-in-guide.pdf", guide_story(), "HARBOR LANE PROPERTIES  ·  Move-in Guide")
    scanned("sample.pdf", "sample-scanned.pdf")
    print("wrote sample.pdf, sample-scanned.pdf, move-in-guide.pdf")
