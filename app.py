"""
Payment Reconciliation Studio
-----------------------------
Turns the findings of my SQL order-payment audit into a money story:
how much is at risk, and what is an automated reconciliation check worth?

Run it with:   python -m streamlit run app.py
"""

import streamlit as st
import plotly.graph_objects as go


# ----------------------------------------------------------------------
# PART 1: THE FACTS (measured in the SQL audit, these never change)
# ----------------------------------------------------------------------
AUDIT = {
    "orders": 99_441,            # orders checked
    "no_items": 772,             # paid, but no items recorded
    "no_items_value": 162_600,   # their total value in R$
    "cancelled": 764,            # of those 772, cancelled or unavailable
    "dup_flagged": 282,          # apparent duplicate payments
    "split": 278,                # of those 282, really split payments
    "mismatched": 1_022,         # mismatched orders listed for review
}


# ----------------------------------------------------------------------
# PART 2: THE ASSUMPTIONS (placeholders until I have real, sourced figures)
# Three ready-made scenarios. Each key is one assumption:
#   p     = chance a refund-pending order turns into a dispute
#   c     = cost of one dispute (R$)
#   k     = share of problems the automated check catches early
#   r     = cost of manually reviewing one flagged order (R$)
#   a     = share of review effort the automation removes
#   run   = yearly cost of running the check (R$)
#   build = one-time cost of building it (R$)
# ----------------------------------------------------------------------
PRESETS = {
    "Conservative": dict(p=0.10, c=40, k=0.60, r=10, a=0.30, run=5_000, build=25_000),
    "Expected":     dict(p=0.20, c=60, k=0.80, r=15, a=0.50, run=3_000, build=15_000),
    "Optimistic":   dict(p=0.30, c=80, k=0.95, r=25, a=0.70, run=2_000, build=10_000),
}


# ----------------------------------------------------------------------
# PART 3: THE MODEL (pure maths, no Streamlit in here)
# Give it the assumptions, get back the money results.
# ----------------------------------------------------------------------
def model(p, c, k, r, a, run, build, rate, months):
    scale = 12 / months                       # turn the audit period into a full year

    cancelled_per_year = AUDIT["cancelled"] * scale
    avg_order_value = AUDIT["no_items_value"] / AUDIT["no_items"]
    exposure = cancelled_per_year * avg_order_value        # money owed back to customers

    # Three ways the check saves money:
    disputes_avoided = cancelled_per_year * p * k * c      # A: fewer costly disputes
    false_alarms = AUDIT["split"] * scale * r              # B: no review of split payments
    review_saved = AUDIT["mismatched"] * scale * r * a     # C: faster review of real mismatches

    benefit = disputes_avoided + false_alarms + review_saved
    net = benefit - run                                    # benefit after yearly running cost

    # Months until the build cost is earned back (None if it never is)
    payback = build / (net / 12) if net > 0 else None

    # 3-year net present value: build cost now, then 3 years of net benefit discounted
    npv = -build + sum(net / (1 + rate) ** year for year in (1, 2, 3))

    return {
        "exposure": exposure, "A": disputes_avoided, "B": false_alarms, "C": review_saved,
        "benefit": benefit, "net": net, "payback": payback, "npv": npv,
    }


def money(x):
    """Short money format: 16169 -> R$16.2K, 750 -> R$750."""
    a = abs(x)
    s = f"{a / 1000:.1f}K" if a >= 1000 else f"{a:.0f}"
    return f"{'−' if x < 0 else ''}R${s}"


# ----------------------------------------------------------------------
# PART 4: THE PAGE
# ----------------------------------------------------------------------
st.set_page_config(page_title="Payment Reconciliation Studio", layout="wide")
st.title("Payment Reconciliation Studio")
st.caption(
    f"Built on a SQL audit of {AUDIT['orders']:,} orders. "
    "All assumptions in the sidebar are placeholders, only the audit counts are measured."
)

# ---- Sidebar: choose a scenario, then fine-tune with sliders ----------
with st.sidebar:
    st.header("Assumptions")
    scenario = st.radio("Scenario", list(PRESETS), index=1, horizontal=True)
    start = PRESETS[scenario]               # the starting values for this scenario

    # The key includes the scenario name, so switching scenario resets the sliders.
    months = st.slider("Audit period (months)", 1, 36, 12, key="months")
    p = st.slider("Dispute probability", 0.0, 0.6, start["p"], 0.01, key=f"p_{scenario}")
    c = st.slider("Cost per dispute (R$)", 10, 200, start["c"], 5, key=f"c_{scenario}")
    k = st.slider("Caught early by automation", 0.0, 1.0, start["k"], 0.01, key=f"k_{scenario}")
    r = st.slider("Review cost per order (R$)", 2, 60, start["r"], 1, key=f"r_{scenario}")
    a = st.slider("Review effort removed", 0.0, 1.0, start["a"], 0.01, key=f"a_{scenario}")
    build = st.slider("Build cost (R$)", 0, 60_000, start["build"], 1_000, key=f"build_{scenario}")
    run = st.slider("Annual run cost (R$)", 0, 20_000, start["run"], 500, key=f"run_{scenario}")
    rate = st.slider("Discount rate", 0.0, 0.2, 0.10, 0.01, key="rate")

# Run the model with whatever the sliders say right now
res = model(p, c, k, r, a, run, build, rate, months)

# ---- Four headline numbers -------------------------------------------
col1, col2, col3, col4 = st.columns(4)
col1.metric("Net benefit per year", f"R${res['net']:,.0f}")
col2.metric("Payback", f"{res['payback']:.1f} months" if res["payback"] else "Never")
col3.metric("3-year NPV", f"R${res['npv']:,.0f}")
col4.metric("Refund exposure per year", f"R${res['exposure']:,.0f}",
            help="Money owed back to customers. It shows the size of the problem, it is not a saving.")

# ---- Chart 1: cumulative gain over 3 years ----------------------------
st.subheader("Cumulative net gain over 3 years")
month_list = list(range(37))                                   # 0, 1, ... 36
cumulative = [-build + res["net"] / 12 * m for m in month_list]  # start at -build, climb by net/12 a month
line = go.Figure(go.Scatter(x=month_list, y=cumulative, mode="lines"))
line.add_hline(y=0)                                            # break-even line
line.update_layout(xaxis_title="Months after launch", yaxis_title="R$")
st.plotly_chart(line, use_container_width=True)

# ---- Chart 2: where the benefit comes from ----------------------------
st.subheader("Annual benefit breakdown")
steps = go.Figure(go.Waterfall(
    x=["Disputes avoided", "False alarms avoided", "Review time saved", "Run cost", "Net"],
    measure=["relative", "relative", "relative", "relative", "total"],
    y=[res["A"], res["B"], res["C"], -run, 0],
))
steps.update_layout(yaxis_title="R$ per year")
st.plotly_chart(steps, use_container_width=True)

# ---- Chart 3: which assumption matters most ---------------------------
st.subheader("Which assumption matters most")
st.caption("Each bar moves ONE assumption from its conservative to its optimistic value "
           "while everything else stays where the sliders are.")

current = dict(p=p, c=c, k=k, r=r, a=a, run=run, build=build, rate=rate, months=months)
names = {
    "p": "Dispute probability", "c": "Cost per dispute", "k": "Early-catch rate",
    "r": "Review cost per order", "a": "Automation share", "run": "Annual run cost",
}

bars = []                                                      # one (label, low, high) per assumption
for key, label in names.items():
    low_case = model(**{**current, key: PRESETS["Conservative"][key]})["net"]
    high_case = model(**{**current, key: PRESETS["Optimistic"][key]})["net"]
    bars.append((label, min(low_case, high_case), max(low_case, high_case)))

bars.sort(key=lambda b: b[2] - b[1])                           # biggest swing on top

tornado = go.Figure(go.Bar(
    y=[b[0] for b in bars],
    x=[b[2] - b[1] for b in bars],                             # bar length = high minus low
    base=[b[1] for b in bars],                                 # bar starts at the low value
    orientation="h",
))
tornado.add_vline(x=res["net"], line_dash="dash")              # where you are now
tornado.update_layout(xaxis_title="Net benefit per year (R$)")
st.plotly_chart(tornado, use_container_width=True)

# ---- The pitch, written from the numbers ------------------------------
st.subheader("The pitch")

payback_text = (f"pays back in {res['payback']:.1f} months" if res["payback"]
                else "does not pay back on these assumptions")
top_label, top_low, top_high = bars[-1]        # the assumption with the biggest swing

# **double stars** make text bold in Streamlit's markdown
pitch = (
    f"**Problem Statement.** Our audit of {AUDIT['orders']:,} orders found "
    f"**{money(res['exposure'])} a year** in payments for orders with no items recorded, "
    f"mostly cancelled orders that need a refund check. It also showed that "
    f"**{AUDIT['split']} of {AUDIT['dup_flagged']} apparent duplicate payments** were really "
    f"split payments, so a naive duplicate rule would send {AUDIT['split']} false alarms to review.\n\n"

    f"**What an automated check does.** For {money(build)} to build and {money(run)} a year to run, "
    f"it would avoid about **{money(res['A'])}** in dispute costs and **{money(res['B'] + res['C'])}** "
    f"in manual review time.\n\n"

    f"**Conclusion.** A net benefit of **{money(res['net'])} a year**; the tool {payback_text}, "
    f"with a 3-year NPV of {money(res['npv'])}. The figure to confirm first is "
    f"**{top_label.lower()}**, because it moves the result most "
    f"(net benefit ranges from {money(top_low)} to {money(top_high)})."
)

with st.container(border=True):
    # Streamlit reads $...$ as maths, so each dollar sign is escaped as \$
    st.markdown(pitch.replace("$", "\\$"))