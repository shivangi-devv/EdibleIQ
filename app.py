
import streamlit as st
import pandas as pd
from datetime import date
from storage import load_data, save_data, load_activity, save_activity
from auth import register_user, authenticate_user
from logic import calculate_days_left, get_priority
from ai_suggestions import generate_recipe_suggestions
import plotly.express as px


# ---------------- PAGE CONFIG ----------------

st.set_page_config(
    page_title="EdibleIQ | Smart Food Management",
    page_icon="🌿",
    layout="wide"
)

if "success_message" not in st.session_state:
    st.session_state.success_message = ""

if "recipe_suggestions" not in st.session_state:
    st.session_state.recipe_suggestions = ""

if "selected_recipe_items" not in st.session_state:
    st.session_state.selected_recipe_items = []


# ---------------- PREMIUM CSS ----------------

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}

.stApp {
    background-color: #F5F8F3;
}

[data-testid="stSidebar"] {
    background-color: #102D24;
}

[data-testid="stSidebar"] * {
    color: #F1F7EF !important;
}

.main-title {
    font-size: 36px;
    font-weight: 800;
    color: #153C2D;
    margin-bottom: 0;
}

.subtitle {
    color: #718579;
    font-size: 15px;
    margin-bottom: 25px;
}

.hero {
    background: linear-gradient(120deg, #123D2E, #247A50);
    padding: 30px;
    border-radius: 18px;
    color: white;
    margin-bottom: 25px;
}

.hero h2 {
    color: white;
    font-size: 27px;
    margin-bottom: 8px;
}

.hero p {
    color: #D9EBDD;
    font-size: 15px;
}

.metric-card {
    background: white;
    padding: 22px;
    border-radius: 15px;
    border: 1px solid #E6EDE5;
    box-shadow: 0 3px 12px rgba(20,60,40,0.04);
}

.metric-label {
    color: #718579;
    font-size: 13px;
    font-weight: 600;
}

.metric-value {
    color: #173D2D;
    font-size: 29px;
    font-weight: 800;
    margin-top: 8px;
}

.section-heading {
    color: #173D2D;
    font-size: 22px;
    font-weight: 750;
    margin-top: 20px;
}

.info-card {
    background: white;
    padding: 18px;
    border: 1px solid #E6EDE5;
    border-radius: 13px;
    margin-bottom: 10px;
}

.stButton > button {
    border-radius: 10px;
    font-weight: 600;
}

div[data-testid="stForm"] {
    background: white;
    padding: 22px;
    border-radius: 15px;
    border: 1px solid #E6EDE5;
}
</style>
""", unsafe_allow_html=True)


# ---------------- LOGIN / SIGNUP ----------------

if "current_user" not in st.session_state:
    st.session_state.current_user = None

if st.session_state.current_user is None:

    st.markdown(
        '<div class="main-title">🌿 Welcome to EdibleIQ</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="subtitle">Sign in or create an account to manage your personal food inventory.</div>',
        unsafe_allow_html=True
    )

    login_tab, signup_tab = st.tabs(
        ["Login", "Create Account"]
    )

    # LOGIN

    with login_tab:

        with st.form("login_form"):

            login_username = st.text_input("Username")

            login_password = st.text_input(
                "Password",
                type="password"
            )

            login_submitted = st.form_submit_button(
                "Login",
                type="primary",
                width="stretch"
            )

            if login_submitted:

                if not login_username.strip() or not login_password:
                    st.error("Please enter your username and password.")

                else:
                    user = authenticate_user(
                        login_username.strip(),
                        login_password
                    )

                    if user:

                        st.session_state.current_user = user

                        st.session_state.success_message = (
                            f"Welcome back, {user['username']}!"
                        )

                        st.rerun()

                    else:
                        st.error("Incorrect username or password.")

    # SIGNUP

    with signup_tab:

        with st.form("signup_form"):

            signup_username = st.text_input(
                "Choose a username"
            )

            signup_email = st.text_input(
                "Email address"
            )

            signup_password = st.text_input(
                "Create password",
                type="password"
            )

            confirm_password = st.text_input(
                "Confirm password",
                type="password"
            )

            signup_submitted = st.form_submit_button(
                "Create Account",
                type="primary",
                width="stretch"
            )

            if signup_submitted:

                if not signup_username.strip() or not signup_email.strip():

                    st.error(
                        "Please enter a username and email address."
                    )

                elif len(signup_password) < 8:

                    st.error(
                        "Password must contain at least 8 characters."
                    )

                elif signup_password != confirm_password:

                    st.error("Passwords do not match.")

                else:

                    success, message = register_user(
                        signup_username.strip(),
                        signup_email.strip(),
                        signup_password
                    )

                    if success:

                        user = authenticate_user(
                            signup_username.strip(),
                            signup_password
                        )

                        st.session_state.current_user = user

                        st.session_state.success_message = message

                        st.rerun()

                    else:
                        st.error(message)

    st.stop()


# ---------------- CURRENT USER ----------------

current_user = st.session_state.current_user
user_id = current_user["user_id"]


# ---------------- HELPER FUNCTIONS ----------------

def get_item_details(item):

    days_left = calculate_days_left(
        item["expiry_date"]
    )

    priority = get_priority(days_left)

    return days_left, priority


def make_inventory_dataframe(food_items):

    rows = []

    for item in food_items:

        days_left, priority = get_item_details(item)

        rows.append({
            "Food Item": item["name"],
            "Quantity": f'{item["quantity"]} {item["unit"]}',
            "Category": item["category"],
            "Expiry Date": item["expiry_date"],
            "Days Left": days_left,
            "Status": priority
        })

    return pd.DataFrame(rows)


def show_page_heading(title, subtitle):

    st.markdown(
        f'<div class="main-title">{title}</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        f'<div class="subtitle">{subtitle}</div>',
        unsafe_allow_html=True
    )


# ---------------- LOAD USER DATA ----------------

food_items = load_data(user_id)


# ---------------- SIDEBAR ----------------

with st.sidebar:

    st.markdown("# 🌿 EdibleIQ")

    st.caption("THINK SMART. WASTE LESS.")

    st.divider()

    selected_page = st.radio(
        "NAVIGATION",
        [
            "Dashboard",
            "Inventory",
            "Add Food",
            "Manage Items",
            "Waste Analytics",
            "AI Recipe Generator"
        ]
    )

    st.divider()

    st.markdown(
        f"**Logged in as:** {current_user['username']}"
    )

    if st.button("Log out", width="stretch"):

        st.session_state.current_user = None

        st.session_state.recipe_suggestions = ""

        st.session_state.selected_recipe_items = []

        st.rerun()

    st.caption("Smart Food Inventory System")


# ---------------- SUCCESS MESSAGE ----------------

if st.session_state.success_message:

    st.success(st.session_state.success_message)

    st.session_state.success_message = ""


# ================= DASHBOARD =================

if selected_page == "Dashboard":

    show_page_heading(
        "Dashboard",
        "Your smart food inventory overview."
    )

    st.markdown("""
    <div class="hero">
        <h2>Welcome to EdibleIQ 🌿</h2>
        <p>Manage your food inventory intelligently.
        Track expiry dates and reduce food waste.</p>
    </div>
    """, unsafe_allow_html=True)

    total_items = len(food_items)

    expired = 0
    expiring_soon = 0
    safe = 0

    for item in food_items:

        days_left, priority = get_item_details(item)

        if priority == "Expired":
            expired += 1

        elif days_left <= 3:
            expiring_soon += 1

        else:
            safe += 1

    col1, col2, col3, col4 = st.columns(4)

    metrics = [
        (col1, "📦 Total Items", total_items),
        (col2, "⚠️ Expiring Soon", expiring_soon),
        (col3, "❌ Expired Items", expired),
        (col4, "✅ Safe Items", safe)
    ]

    for col, label, value in metrics:

        with col:

            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">{label}</div>
                <div class="metric-value">{value}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown(
        '<div class="section-heading">Expiry Alerts</div>',
        unsafe_allow_html=True
    )

    alerts = []

    for item in food_items:

        days_left, priority = get_item_details(item)

        if priority in ["Expired", "Expiring Today", "High"]:

            alerts.append(
                (item, days_left, priority)
            )

    if alerts:

        for item, days_left, priority in alerts:

            if priority == "Expired":

                st.error(
                    f'❌ {item["name"]} has expired.'
                )

            elif priority == "Expiring Today":

                st.warning(
                    f'⚠️ {item["name"]} expires today!'
                )

            else:

                st.warning(
                    f'⚠️ {item["name"]} expires in {days_left} days.'
                )

    else:

        st.success(
            "No urgent expiry alerts. Your inventory looks good!"
        )

    st.markdown(
        '<div class="section-heading">Recent Inventory</div>',
        unsafe_allow_html=True
    )

    if food_items:

        df = make_inventory_dataframe(food_items)

        st.dataframe(
            df,
            width="stretch",
            hide_index=True
        )

    else:

        st.info(
            "Your inventory is empty. Add some food items to get started."
        )


# ================= WASTE ANALYTICS =================

elif selected_page == "Waste Analytics":

    show_page_heading(
        "Waste Analytics",
        "Understand your food usage and waste patterns."
    )

    activities = load_activity(user_id)

    if activities:

        df = pd.DataFrame(activities)

        used_df = df[df["activity"] == "Used"]

        wasted_df = df[df["activity"] == "Wasted"]

        col1, col2, col3 = st.columns(3)

        with col1:

            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">🍽️ Used Records</div>
                <div class="metric-value">{len(used_df)}</div>
            </div>
            """, unsafe_allow_html=True)

        with col2:

            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">🗑️ Wasted Records</div>
                <div class="metric-value">{len(wasted_df)}</div>
            </div>
            """, unsafe_allow_html=True)

        with col3:

            waste_share = (
                len(wasted_df) / len(df) * 100
                if len(df) > 0 else 0
            )

            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Waste Activity Share</div>
                <div class="metric-value">{waste_share:.1f}%</div>
            </div>
            """, unsafe_allow_html=True)

        st.caption(
            "Waste Activity Share is based on recorded activity entries, "
            "not the total quantity of food."
        )

        st.markdown(
            '<div class="section-heading">Quantity by Unit</div>',
            unsafe_allow_html=True
        )

        unit_summary = (
            df.groupby(["unit", "activity"])["quantity"]
            .sum()
            .reset_index()
        )

        if not unit_summary.empty:

            fig = px.bar(
                unit_summary,
                x="unit",
                y="quantity",
                color="activity",
                barmode="group",
                title="Food Used vs Wasted by Unit",
                color_discrete_map={
                    "Used": "#239B68",
                    "Wasted": "#E47B65"
                },
                labels={
                    "unit": "Unit",
                    "quantity": "Quantity",
                    "activity": "Activity"
                }
            )

            fig.update_layout(
                plot_bgcolor="white",
                paper_bgcolor="white",
                font_color="#173D2D",
                legend_title_text="Food Activity"
            )

            st.plotly_chart(
                fig,
                width="stretch"
            )

        st.markdown(
            '<div class="section-heading">Category-wise Waste</div>',
            unsafe_allow_html=True
        )

        if not wasted_df.empty:

            category_summary = (
                wasted_df.groupby("category")["quantity"]
                .sum()
                .reset_index()
            )

            fig2 = px.bar(
                category_summary,
                x="category",
                y="quantity",
                color="category",
                title="Food Waste by Category",
                labels={
                    "category": "Food Category",
                    "quantity": "Wasted Quantity"
                }
            )

            fig2.update_layout(
                plot_bgcolor="white",
                paper_bgcolor="white",
                showlegend=False,
                font_color="#173D2D"
            )

            st.plotly_chart(
                fig2,
                width="stretch"
            )

        else:

            st.success(
                "No wasted food recorded yet!"
            )

        # ---------------- WEEKLY TRENDS ----------------

        df["date"] = pd.to_datetime(df["date"])

        st.markdown(
            '<div class="section-heading">📅 Weekly Food Trends</div>',
            unsafe_allow_html=True
        )

        today = pd.Timestamp(date.today())

        week_start = today - pd.Timedelta(days=6)

        weekly_df = df[
            (df["date"] >= week_start) &
            (df["date"] <= today)
        ].copy()

        if not weekly_df.empty:

            weekly_summary = (
                weekly_df.groupby(
                    ["date", "unit", "activity"]
                )["quantity"]
                .sum()
                .reset_index()
            )

            weekly_summary["date_label"] = (
                pd.to_datetime(
                    weekly_summary["date"]
                ).dt.strftime("%d %b")
            )

            weekly_chart = px.bar(
                weekly_summary,
                x="date_label",
                y="quantity",
                color="activity",
                facet_col="unit",
                barmode="group",
                title="Food Used vs Wasted - Last 7 Days",
                color_discrete_map={
                    "Used": "#239B68",
                    "Wasted": "#E47B65"
                }
            )

            st.plotly_chart(
                weekly_chart,
                width="stretch"
            )

        else:

            st.info(
                "No activity recorded in the last 7 days."
            )

        # ---------------- MONTHLY TRENDS ----------------

        st.markdown(
            '<div class="section-heading">📊 Monthly Food Trends</div>',
            unsafe_allow_html=True
        )

        df["month"] = df["date"].dt.strftime("%Y-%m")

        monthly_summary = (
            df.groupby(
                ["month", "unit", "activity"]
            )["quantity"]
            .sum()
            .reset_index()
        )

        monthly_summary["month"] = (
            pd.to_datetime(
                monthly_summary["month"]
            ).dt.strftime("%b %Y")
        )

        monthly_chart = px.bar(
            monthly_summary,
            x="month",
            y="quantity",
            color="activity",
            facet_col="unit",
            barmode="group",
            title="Monthly Food Usage vs Waste",
            color_discrete_map={
                "Used": "#239B68",
                "Wasted": "#E47B65"
            }
        )

        st.plotly_chart(
            monthly_chart,
            width="stretch"
        )

        st.markdown(
            '<div class="section-heading">Activity History</div>',
            unsafe_allow_html=True
        )

        history = df[
            ["name", "quantity", "unit", "category", "activity", "date"]
        ].copy()

        history.columns = [
            "Food Item",
            "Quantity",
            "Unit",
            "Category",
            "Activity",
            "Date"
        ]

        history = history.sort_values(
            "Date",
            ascending=False
        )

        st.dataframe(
            history,
            width="stretch",
            hide_index=True
        )

    else:

        st.info(
            "No food activity recorded yet. "
            "Go to Manage Items and mark food as Used or Wasted "
            "to see your analytics."
        )


# ================= INVENTORY =================

elif selected_page == "Inventory":

    show_page_heading(
        "Food Inventory",
        "View and track all your stored food items."
    )

    if food_items:

        df = make_inventory_dataframe(food_items)

        search = st.text_input(
            "🔍 Search food items"
        )

        if search:

            df = df[
                df["Food Item"].str.contains(
                    search,
                    case=False,
                    na=False
                )
            ]

        st.dataframe(
            df,
            width="stretch",
            hide_index=True
        )

        st.caption(
            f"Showing {len(df)} food items."
        )

    else:

        st.info(
            "No food items available. Add your first item!"
        )


# ================= ADD FOOD =================

elif selected_page == "Add Food":

    show_page_heading(
        "Add Food Item",
        "Add a new item to your smart inventory."
    )

    with st.form(
        "add_food_form",
        clear_on_submit=True
    ):

        name = st.text_input(
            "Food Item Name"
        )

        col1, col2 = st.columns(2)

        with col1:

            quantity = st.number_input(
                "Quantity",
                min_value=0.1,
                value=1.0,
                step=0.5
            )

        with col2:

            unit = st.selectbox(
                "Unit",
                ["kg", "g", "litre", "ml", "pieces", "packets"]
            )

        category = st.selectbox(
            "Category",
            [
                "Vegetables",
                "Fruits",
                "Dairy",
                "Grains",
                "Bakery",
                "Other"
            ]
        )

        expiry_date = st.date_input(
            "Expiry Date",
            min_value=date.today()
        )

        submitted = st.form_submit_button(
            "➕ Add to Inventory",
            type="primary",
            width="stretch"
        )

        if submitted:

            if not name.strip():

                st.error(
                    "Please enter a food item name."
                )

            elif any(
                item["name"].strip().lower() == name.strip().lower()
                for item in food_items
            ):

                st.error(
                    "This food item already exists. Please edit its quantity instead."
                )

            else:

                new_item = {
                    "name": name.strip(),
                    "quantity": quantity,
                    "unit": unit,
                    "category": category,
                    "expiry_date": expiry_date.isoformat()
                }

                food_items.append(new_item)

                save_data(food_items, user_id)

                st.session_state.success_message = (
                    f"{name} added successfully!"
                )

                st.rerun()


# ================= MANAGE ITEMS =================

elif selected_page == "Manage Items":

    show_page_heading(
        "Manage Inventory",
        "Edit or delete your existing food items."
    )

    if food_items:

        food_names = [
            item["name"] for item in food_items
        ]

        selected_name = st.selectbox(
            "Select Food Item",
            food_names
        )

        selected_item = next(
            item for item in food_items
            if item["name"] == selected_name
        )

        st.markdown(
            "### Edit Food Details"
        )

        with st.form("edit_food_form"):

            edited_name = st.text_input(
                "Food Name",
                value=selected_item["name"]
            )

            col1, col2 = st.columns(2)

            with col1:

                edited_quantity = st.number_input(
                    "Quantity",
                    min_value=0.1,
                    value=float(selected_item["quantity"]),
                    step=0.5
                )

            with col2:

                units = [
                    "kg", "g", "litre", "ml", "pieces", "packets"
                ]

                current_unit = selected_item["unit"]

                edited_unit = st.selectbox(
                    "Unit",
                    units,
                    index=units.index(current_unit)
                    if current_unit in units else 0
                )

            categories = [
                "Vegetables",
                "Fruits",
                "Dairy",
                "Grains",
                "Bakery",
                "Other"
            ]

            current_category = selected_item["category"]

            edited_category = st.selectbox(
                "Category",
                categories,
                index=categories.index(current_category)
                if current_category in categories else 0
            )

            edited_expiry = st.date_input(
                "Expiry Date",
                value=date.fromisoformat(
                    selected_item["expiry_date"]
                )
            )

            update = st.form_submit_button(
                "💾 Update Item",
                type="primary",
                width="stretch"
            )

            if update:

                if not edited_name.strip():

                    st.error(
                        "Food name cannot be empty."
                    )

                elif any(
                    item["name"].strip().lower() == edited_name.strip().lower()
                    and item is not selected_item
                    for item in food_items
                ):

                    st.error(
                        "Another item already has this name."
                    )

                else:

                    selected_item["name"] = edited_name.strip()

                    selected_item["quantity"] = edited_quantity

                    selected_item["unit"] = edited_unit

                    selected_item["category"] = edited_category

                    selected_item["expiry_date"] = edited_expiry.isoformat()

                    save_data(food_items, user_id)

                    st.session_state.success_message = (
                        f"{edited_name} updated successfully!"
                    )

                    st.rerun()

        st.divider()

        st.markdown(
            "### 🍽️ Track Food Activity"
        )

        st.write(
            "Record how much food you used or wasted."
        )

        available_quantity = float(
            selected_item["quantity"]
        )

        with st.form("food_activity_form"):

            activity_type = st.radio(
                "Activity",
                ["Used", "Wasted"],
                horizontal=True
            )

            activity_quantity = st.number_input(
                "Quantity",
                min_value=0.1,
                max_value=available_quantity,
                value=min(1.0, available_quantity),
                step=0.1
            )

            activity_submit = st.form_submit_button(
                "Save Food Activity",
                type="primary",
                width="stretch"
            )

            if activity_submit:

                activities = load_activity(user_id)

                activities.append({
                    "name": selected_item["name"],
                    "quantity": activity_quantity,
                    "unit": selected_item["unit"],
                    "category": selected_item["category"],
                    "activity": activity_type,
                    "date": date.today().isoformat()
                })

                save_activity(
                    activities,
                    user_id
                )

                remaining = (
                    available_quantity - activity_quantity
                )

                if remaining <= 0.000001:

                    food_items.remove(selected_item)

                else:

                    selected_item["quantity"] = round(
                        remaining,
                        3
                    )

                save_data(
                    food_items,
                    user_id
                )

                st.session_state.success_message = (
                    f"{activity_quantity} {selected_item['unit']} "
                    f"recorded as {activity_type}!"
                )

                st.rerun()

        st.markdown(
            "### Delete Food Item"
        )

        st.warning(
            f'You are about to delete {selected_item["name"]} from inventory.'
        )

        confirm_delete = st.checkbox(
            "I confirm that I want to delete this item."
        )

        if st.button(
            "🗑️ Delete Item",
            type="primary",
            disabled=not confirm_delete
        ):

            food_items.remove(selected_item)

            save_data(
                food_items,
                user_id
            )

            st.session_state.success_message = (
                f"{selected_name} deleted successfully!"
            )

            st.rerun()

    else:

        st.info(
            "Your inventory is empty. Add food items first."
        )


# ================= AI RECIPE GENERATOR =================

elif selected_page == "AI Recipe Generator":

    show_page_heading(
        "AI Recipe Generator",
        "Choose your ingredients and discover recipes with AI."
    )

    st.markdown("""
    <div class="hero">
        <h2>🍳 Cook Smart with EdibleIQ</h2>
        <p>Select the ingredients you want to use.
        Our AI will suggest recipes using only your selected ingredients.</p>
    </div>
    """, unsafe_allow_html=True)

    if food_items:

        st.markdown(
            "### 🥗 Select Your Ingredients"
        )

        st.write(
            "Choose the food items you want to use for your recipe."
        )

        available_names = [
            item["name"] for item in food_items
        ]

        selected_ingredients = st.multiselect(
            "Choose ingredients from your inventory",
            options=available_names,
            default=[
                name for name in st.session_state.selected_recipe_items
                if name in available_names
            ],
            placeholder="Select one or more ingredients..."
        )

        st.session_state.selected_recipe_items = selected_ingredients

        if selected_ingredients:

            st.markdown(
                "### Your Selected Ingredients"
            )

            ingredient_columns = st.columns(3)

            for index, ingredient in enumerate(selected_ingredients):

                with ingredient_columns[index % 3]:

                    st.markdown(f"""
                    <div class="info-card">
                        🌿 <b>{ingredient}</b>
                    </div>
                    """, unsafe_allow_html=True)

            st.caption(
                f"{len(selected_ingredients)} ingredients selected."
            )

            if st.button(
                "✨ Generate Recipes",
                type="primary",
                width="stretch"
            ):

                selected_food_items = [
                    item for item in food_items
                    if item["name"] in selected_ingredients
                ]

                with st.spinner(
                    "🌿 EdibleIQ is preparing your recipes..."
                ):

                    suggestions = generate_recipe_suggestions(
                        selected_food_items
                    )

                st.session_state.recipe_suggestions = suggestions

            if st.session_state.recipe_suggestions:

                st.divider()

                st.markdown(
                    "### 🍽️ Your Recipe Suggestions"
                )

                st.markdown(
                    st.session_state.recipe_suggestions
                )

        else:

            st.info(
                "Select at least one ingredient to generate recipes."
            )

    else:

        st.warning(
            "Your inventory is empty. Add food items first "
            "to generate recipes."
        )


# ---------------- FOOTER ----------------

st.markdown("""
<br>
<hr>
<div style="text-align:center; color:#84958A; font-size:12px;">
    EdibleIQ 🌿 | Think Smart. Waste Less.
    <br>
    Smart Food Inventory & Waste Management System
</div>
""", unsafe_allow_html=True)
