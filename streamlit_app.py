import datetime
import random

import altair as alt
import numpy as np
import pandas as pd
import streamlit as st

# Show app title and description.
st.set_page_config(page_title="支持工单", page_icon="🎫")
st.title("🎫 支持工单系统")
st.write(
    """
    此应用程序展示了如何使用Streamlit构建内部工具。这里我们实现了一个支持工单工作流程，
    用户可以创建工单、编辑现有工单并查看相关统计数据。
    """
)

# Create a random Pandas dataframe with existing tickets.
if "df" not in st.session_state:

    # Set seed for reproducibility.
    np.random.seed(42)

    # Make up some fake issue descriptions.
    issue_descriptions = [
        "办公室网络连接问题",
        "软件启动时崩溃",
        "打印机无法响应打印命令",
        "邮件服务器宕机",
        "数据备份失败",
        "登录验证问题",
        "网站性能下降",
        "发现安全漏洞",
        "服务器机房硬件故障",
        "员工无法访问共享文件",
        "数据库连接失败",
        "移动应用数据同步异常",
        "网络电话系统问题",
        "远程员工VPN连接问题",
        "系统更新导致兼容性问题",
        "文件服务器存储空间不足",
        "入侵检测系统警报",
        "库存管理系统错误",
        "CRM客户数据无法加载",
        "协作工具无法发送通知",
    ]

    # Generate the dataframe with 100 rows/tickets.
    data = {
        "ID": [f"TICKET-{i}" for i in range(1100, 1000, -1)],
        "Issue": np.random.choice(issue_descriptions, size=100),
        "Status": np.random.choice(["待处理", "处理中", "已关闭"], size=100),
        "Priority": np.random.choice(["高", "中", "低"], size=100),
        "Date Submitted": [
            datetime.date(2023, 6, 1) + datetime.timedelta(days=random.randint(0, 182))
            for _ in range(100)
        ],
    }
    df = pd.DataFrame(data)

    # Save the dataframe in session state (a dictionary-like object that persists across
    # page runs). This ensures our data is persisted when the app updates.
    st.session_state.df = df


# Show a section to add a new ticket.
st.header("添加工单")

# We're adding tickets via an `st.form` and some input widgets. If widgets are used
# in a form, the app will only rerun once the submit button is pressed.
with st.form("add_ticket_form"):
    issue = st.text_area("问题描述")
    priority = st.selectbox("优先级", ["高", "中", "低"])
    submitted = st.form_submit_button("提交")

if submitted:
    # Make a dataframe for the new ticket and append it to the dataframe in session
    # state.
    recent_ticket_number = int(max(st.session_state.df.ID).split("-")[1])
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    df_new = pd.DataFrame(
        [
            {
                "ID": f"TICKET-{recent_ticket_number+1}",
                "Issue": issue,
                "Status": "待处理",
                "Priority": priority,
                "Date Submitted": today,
            }
        ]
    )

    # Show a little success message.
    st.write("工单已提交！以下是工单详情：")
    st.dataframe(df_new, use_container_width=True, hide_index=True)
    st.session_state.df = pd.concat([df_new, st.session_state.df], axis=0)

# Show section to view and edit existing tickets in a table.
st.header("现有工单")
st.write(f"工单数量: `{len(st.session_state.df)}`")

st.info(
    "您可以通过双击单元格来编辑工单。请注意下方图表会自动更新！您也可以通过点击列标题对表格进行排序。",
    icon="✍️",
)

# Show the tickets dataframe with `st.data_editor`. This lets the user edit the table
# cells. The edited data is returned as a new dataframe.
edited_df = st.data_editor(
    st.session_state.df,
    use_container_width=True,
    hide_index=True,
    column_config={
        "Status": st.column_config.SelectboxColumn(
            "状态",
            help="工单状态",
            options=["待处理", "处理中", "已关闭"],
            required=True,
        ),
        "Priority": st.column_config.SelectboxColumn(
            "优先级",
            help="优先级",
            options=["高", "中", "低"],
            required=True,
        ),
    },
    # Disable editing the ID and Date Submitted columns.
    disabled=["ID", "Date Submitted"],
)

# Show some metrics and charts about the ticket.
st.header("统计数据")

# Show metrics side by side using `st.columns` and `st.metric`.
col1, col2, col3 = st.columns(3)
num_open_tickets = len(st.session_state.df[st.session_state.df.Status == "待处理"])
col1.metric(label="未解决工单数", value=num_open_tickets, delta=10)
col2.metric(label="首次响应时间（小时）", value=5.2, delta=-1.5)
col3.metric(label="平均解决时间（小时）", value=16, delta=2)

# Show two Altair charts using `st.altair_chart`.
st.write("")
st.write("##### 每月工单状态")
status_plot = (
    alt.Chart(edited_df)
    .mark_bar()
    .encode(
        x="month(Date Submitted):O",
        y="count():Q",
        xOffset="Status:N",
        color="Status:N",
    )
    .configure_legend(
        orient="bottom", titleFontSize=14, labelFontSize=14, titlePadding=5
    )
)
st.altair_chart(status_plot, use_container_width=True, theme="streamlit")

st.write("##### 当前工单优先级")
priority_plot = (
    alt.Chart(edited_df)
    .mark_arc()
    .encode(theta="count():Q", color="Priority:N")
    .properties(height=300)
    .configure_legend(
        orient="bottom", titleFontSize=14, labelFontSize=14, titlePadding=5
    )
)
st.altair_chart(priority_plot, use_container_width=True, theme="streamlit")