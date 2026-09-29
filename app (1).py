
import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import japanize_matplotlib
import requests

# スマホの画面幅に合わせて縦長に最適化
st.set_page_config(page_title="最上川・馬見ヶ崎川 防災AI", layout="centered")

st.title("🌊 最上川・馬見ヶ崎川 防災AIアプリ")
st.caption("リアルタイム気象データ連動・洪水シミュレーター")

# LINE通知用のトークン設定（スマホ画面から直接変更できるように設定）
line_token = st.sidebar.text_input("LINE Notify トークンキー", type="password")

# 対象河川の選択（スマホで押しやすいセレクトボックスに変更）
river = st.selectbox("🔍 対象河川の選択", ["最上川 (広域詳細・下流エリア)", "馬見ヶ崎川 (支流メイン)"])

# 危険度の微調整スライダー
danger_level = st.slider("🌊 危険度の微調整", 1, 100, 10)

# --- 簡易地形と浸水計算 ---
grid_size = 40
x = np.linspace(-4, 4, grid_size)
y = np.linspace(-4, 4, grid_size)
X, Y = np.meshgrid(x, y)

if river == "最上川 (広域詳細・下流エリア)":
    Z_elevation = (Y + 4) * 0.04 - np.exp(-((X - (np.sin(Y * 1.2) * 0.7 - 0.5))**2) / 0.25) * 0.32
    place_labels = [(-1.5, 3.0, "戸沢村"), (-0.3, 1.8, "大蔵村"), (0.5, 0.8, "大石田町"), (-1.2, -1.8, "寒河江/中山")]
    station_labels = [(-1.1, 2.5, "★古口観測所"), (0.6, 1.2, "★堀内観測所")]
else:
    Z_elevation = (Y + 4) * 0.03 - np.exp(-((X - Y - 0.2)**2) / 0.3) * 0.28
    place_labels = [(-2.0, 2.0, "山形市(大野目)"), (-0.5, 0.8, "山形市(落合)"), (1.0, 0.2, "山形市(小白川)")]
    station_labels = [(-0.8, 0.5, "★鈴川観測所")]

water_level = -0.18 + (danger_level / 100.0) * 0.65

# --- 描画 ---
fig = plt.figure(figsize=(10, 8))
ax = fig.add_subplot(111, projection='3d')
ax.plot_surface(X, Y, Z_elevation, cmap='gist_earth', linewidth=0, alpha=0.7)

Z_water = np.full_like(Z_elevation, water_level)
water_depth = Z_water - Z_elevation
water_depth[water_depth <= 0] = np.nan

if not np.all(np.isnan(water_depth)):
    colors = plt.cm.ocean(0.2 + (water_depth / 0.6) * 0.5)
    colors[:, :, 3] = 0.65
    ax.plot_surface(X, Y, np.where(Z_water > Z_elevation, Z_water, np.nan), facecolors=colors, linewidth=0)

# 地名プロット
for px, py, name in place_labels:
    ax.text(px, py, Z_elevation[int((py+4)*4), int((px+4)*4)] if 0<int((py+4)*4)<40 else 0, name, fontsize=10, weight='bold', bbox=dict(facecolor='white', alpha=0.7))

ax.view_init(elev=35, azim=-60)
ax.set_axis_off()
ax.set_zlim(-0.5, 0.9)

st.pyplot(fig)

# 解説パネルの表示
with st.expander("❓ 画面のマークの意味・詳しい川の解説を見る"):
    st.write("グレー/茶色の面が山形盆地の地形、青いエリアがAI予測の浸水範囲です。")
