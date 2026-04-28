import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns

# ─────────────────────────────────────────────
#  Page config
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Bike Sharing Dashboard",
    page_icon="🚲",
    layout="wide",
)

# ─────────────────────────────────────────────
#  Load & clean data
# ─────────────────────────────────────────────
@st.cache_data
def load_data():
    day_df  = pd.read_csv("dashboard/main_data.csv", parse_dates=["dteday"])
    hour_df = pd.read_csv("dashboard/hour_data.csv", parse_dates=["dteday"])
    return day_df, hour_df

day_df, hour_df = load_data()

# ─────────────────────────────────────────────
#  Sidebar — filter
# ─────────────────────────────────────────────
st.sidebar.image(
    "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e0/Bike_sharing_station.jpg/320px-Bike_sharing_station.jpg",
    use_container_width=True,
)
st.sidebar.title("🔍 Filter Data")

year_opts = sorted(day_df["yr"].unique())
sel_year  = st.sidebar.multiselect("Tahun", year_opts, default=year_opts)

season_opts = day_df["season"].cat.categories.tolist()
sel_season  = st.sidebar.multiselect("Musim", season_opts, default=season_opts)

# Apply filters
mask_day  = day_df["yr"].isin(sel_year)  & day_df["season"].isin(sel_season)
mask_hour = hour_df["yr"].isin(sel_year) & hour_df["season"].isin(sel_season)
fday  = day_df[mask_day]
fhour = hour_df[mask_hour]

# ─────────────────────────────────────────────
#  Header
# ─────────────────────────────────────────────
st.title("🚲 Bike Sharing — Analisis Data Dashboard")
st.markdown(
    "**Dataset:** Capital Bikeshare Washington D.C., USA (2011–2012)  \n"
    "Dashboard ini menyajikan eksplorasi interaktif pola penyewaan sepeda berdasarkan "
    "waktu, musim, dan kondisi cuaca."
)
st.divider()

# ─────────────────────────────────────────────
#  KPI Cards
# ─────────────────────────────────────────────
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Penyewaan", f"{fday['cnt'].sum():,}")
col2.metric("Rata-rata Harian", f"{fday['cnt'].mean():,.0f}")
col3.metric("Penyewaan Tertinggi (1 Hari)", f"{fday['cnt'].max():,}")
col4.metric("Penyewaan Terendah (1 Hari)", f"{fday['cnt'].min():,}")

st.divider()

# ─────────────────────────────────────────────
#  Pertanyaan 1 — Pola Per Jam
# ─────────────────────────────────────────────
st.subheader("📌 Pertanyaan 1: Pola Penyewaan Per Jam Berdasarkan Tipe Hari")

hourly = (
    fhour.groupby(["hr", "workingday"], observed=True)["cnt"]
    .mean()
    .reset_index()
)
hourly["day_type"] = hourly["workingday"].map({1: "Hari Kerja", 0: "Hari Libur/Akhir Pekan"})

fig1, ax1 = plt.subplots(figsize=(11, 4))
for dtype, color, marker in [("Hari Kerja", "#2196F3", "o"), ("Hari Libur/Akhir Pekan", "#FF9800", "s")]:
    sub = hourly[hourly["day_type"] == dtype]
    ax1.plot(sub["hr"], sub["cnt"], marker=marker, markersize=5,
             linewidth=2.2, color=color, label=dtype)

ax1.axvspan(7.5, 9.5,   alpha=0.08, color="#2196F3")
ax1.axvspan(16.5, 18.5, alpha=0.08, color="#2196F3")
ax1.set_title("Rata-rata Penyewaan Sepeda per Jam (Hari Kerja vs. Hari Libur/Akhir Pekan)",
              fontsize=12, fontweight="bold")
ax1.set_xlabel("Jam (0–23)", fontsize=10)
ax1.set_ylabel("Rata-rata Jumlah Penyewaan", fontsize=10)
ax1.set_xticks(range(0, 24))
ax1.legend(fontsize=9)
ax1.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{int(x):,}"))
ax1.spines["top"].set_visible(False)
ax1.spines["right"].set_visible(False)
plt.tight_layout()
st.pyplot(fig1)

with st.expander("💡 Insight Pertanyaan 1"):
    st.write(
        "- Hari kerja menunjukkan pola **bimodal** (dua puncak) di pukul **08:00** dan **17:00–18:00**, "
        "mencerminkan perilaku komuter.\n"
        "- Hari libur memiliki pola puncak tunggal di siang hari (pukul **12:00–14:00**) "
        "untuk aktivitas rekreasional.\n"
        "- Zona biru muda menandai jam sibuk hari kerja yang perlu ketersediaan sepeda ekstra."
    )

st.divider()

# ─────────────────────────────────────────────
#  Pertanyaan 2 — Musim & Cuaca
# ─────────────────────────────────────────────
st.subheader("📌 Pertanyaan 2: Pengaruh Musim & Kondisi Cuaca terhadap Penyewaan Harian")

tab1, tab2 = st.tabs(["Bar Chart", "Heatmap"])

SEASON_COLORS  = {"Spring": "#81C784", "Summer": "#FFB74D", "Fall": "#EF5350", "Winter": "#64B5F6"}
WEATHER_COLORS = {"Clear": "#FDD835", "Mist/Cloudy": "#90CAF9", "Light Rain/Snow": "#CE93D8", "Heavy Rain/Snow": "#BDBDBD"}

with tab1:
    c1, c2 = st.columns(2)

    # Season bar
    season_agg = (
        fday.groupby("season", observed=True)["cnt"]
        .mean()
        .sort_values(ascending=False)
    )
    with c1:
        fig2, ax2 = plt.subplots(figsize=(5.5, 4))
        bars = ax2.bar(season_agg.index, season_agg.values,
                       color=[SEASON_COLORS.get(s, "#90A4AE") for s in season_agg.index],
                       edgecolor="#555", linewidth=0.6, width=0.55)
        for bar in bars:
            ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 30,
                     f"{bar.get_height():,.0f}", ha="center", va="bottom", fontsize=8.5, fontweight="bold")
        ax2.set_title("Rata-rata Penyewaan Harian per Musim", fontsize=10, fontweight="bold")
        ax2.set_xlabel("Musim", fontsize=9)
        ax2.set_ylabel("Rata-rata Penyewaan", fontsize=9)
        ax2.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x,_: f"{int(x):,}"))
        ax2.set_ylim(0, season_agg.max() * 1.18)
        ax2.spines["top"].set_visible(False)
        ax2.spines["right"].set_visible(False)
        plt.tight_layout()
        st.pyplot(fig2)

    # Weather bar
    weather_agg = (
        fday.groupby("weathersit", observed=True)["cnt"]
        .mean()
        .sort_values(ascending=False)
    )
    with c2:
        fig3, ax3 = plt.subplots(figsize=(5.5, 4))
        bars3 = ax3.bar(weather_agg.index, weather_agg.values,
                        color=[WEATHER_COLORS.get(w, "#BDBDBD") for w in weather_agg.index],
                        edgecolor="#555", linewidth=0.6, width=0.45)
        for bar in bars3:
            ax3.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 30,
                     f"{bar.get_height():,.0f}", ha="center", va="bottom", fontsize=8.5, fontweight="bold")
        ax3.set_title("Rata-rata Penyewaan Harian per Kondisi Cuaca", fontsize=10, fontweight="bold")
        ax3.set_xlabel("Kondisi Cuaca", fontsize=9)
        ax3.set_ylabel("Rata-rata Penyewaan", fontsize=9)
        ax3.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x,_: f"{int(x):,}"))
        ax3.set_ylim(0, weather_agg.max() * 1.18)
        ax3.tick_params(axis="x", labelsize=7.5)
        ax3.spines["top"].set_visible(False)
        ax3.spines["right"].set_visible(False)
        plt.tight_layout()
        st.pyplot(fig3)

with tab2:
    heatmap_data = (
        fday.groupby(["season", "weathersit"], observed=True)["cnt"]
        .mean()
        .round(0)
        .unstack(level="weathersit")
    )
    season_order = ["Spring", "Summer", "Fall", "Winter"]
    heatmap_data = heatmap_data.reindex([s for s in season_order if s in heatmap_data.index])

    fig4, ax4 = plt.subplots(figsize=(9, 4))
    sns.heatmap(heatmap_data, annot=True, fmt=".0f", cmap="YlOrRd",
                linewidths=0.5, linecolor="#ddd",
                cbar_kws={"label": "Rata-rata Penyewaan Harian"}, ax=ax4)
    ax4.set_title("Heatmap Rata-rata Penyewaan Harian per Musim & Kondisi Cuaca",
                  fontsize=11, fontweight="bold", pad=10)
    ax4.set_xlabel("Kondisi Cuaca", fontsize=9)
    ax4.set_ylabel("Musim", fontsize=9)
    plt.tight_layout()
    st.pyplot(fig4)

with st.expander("💡 Insight Pertanyaan 2"):
    st.write(
        "- **Musim gugur (Fall)** menghasilkan rata-rata penyewaan harian tertinggi.\n"
        "- **Cuaca cerah (Clear)** secara konsisten meningkatkan penyewaan di semua musim.\n"
        "- Kombinasi **Fall + Clear** adalah skenario permintaan tertinggi.\n"
        "- Hujan/salju dapat memangkas permintaan hingga **>40%** dibandingkan cuaca cerah."
    )

st.divider()

# ─────────────────────────────────────────────
#  Tren Harian (bonus chart)
# ─────────────────────────────────────────────
st.subheader("📈 Tren Total Penyewaan Sepeda Harian")

fig5, ax5 = plt.subplots(figsize=(12, 3.5))
ax5.plot(fday["dteday"], fday["cnt"], color="#1E88E5", linewidth=1, alpha=0.7)
ax5.fill_between(fday["dteday"], fday["cnt"], alpha=0.12, color="#1E88E5")
ax5.set_title("Tren Penyewaan Sepeda Harian (2011–2012)", fontsize=11, fontweight="bold")
ax5.set_xlabel("Tanggal", fontsize=9)
ax5.set_ylabel("Total Penyewaan", fontsize=9)
ax5.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x,_: f"{int(x):,}"))
ax5.spines["top"].set_visible(False)
ax5.spines["right"].set_visible(False)
plt.tight_layout()
st.pyplot(fig5)

# ─────────────────────────────────────────────
#  Footer
# ─────────────────────────────────────────────
st.divider()
st.caption("Dashboard dibuat untuk Proyek Analisis Data — Dicoding | Dataset: Capital Bikeshare Washington D.C. (2011–2012)")
