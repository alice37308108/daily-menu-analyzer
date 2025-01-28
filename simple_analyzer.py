import pandas as pd
import numpy as np


def analyze_menu_popularity_simple(sales_data, prepared_data):
    """
    日替わりメニューの人気度を分析する関数（シンプル版）
    daily_special_sales（日替わり販売数）のみで分析

    Parameters:
    sales_data: 販売データのDataFrame（時間帯ごとの販売数）
    prepared_data: 作成数データのDataFrame（日ごとの作成数）
    """
    # 時間帯ごとの重み付け
    time_weights = {
        '11:00-11:30': 2.0,
        '11:30-12:00': 1.5,
        '12:00-12:30': 1.0,
        '12:30-13:00': 0.5
    }

    results = []

    for date in sales_data['date'].unique():
        # その日のデータを抽出
        menu_data = sales_data[sales_data['date'] == date]
        prepared = prepared_data[prepared_data['date'] == date].iloc[0]

        menu_name = prepared['menu_name']
        total_prepared = prepared['prepared_amount']

        # 時間帯ごとの販売数の割合を計算
        time_scores = []
        early_sales = 0  # 前半（11:00-12:00）の販売数
        total_sales = 0  # 総販売数

        max_possible_per_slot = total_prepared / len(time_weights)  # 理想的な時間帯あたりの販売数

        for idx, row in menu_data.iterrows():
            # 時間帯ごとの販売数を理想値との比率で評価（100点満点）
            sales_score = (row['daily_special_sales'] / max_possible_per_slot) * 100
            # 上限を100点とする
            sales_score = min(sales_score, 100)

            # スコアに時間帯の重みを掛ける
            weighted_score = sales_score * time_weights[row['time_slot']]
            time_scores.append(weighted_score)

            # 前半の販売数を集計
            if row['time_slot'] in ['11:00-11:30', '11:30-12:00']:
                early_sales += row['daily_special_sales']

            # 総販売数を集計
            total_sales += row['daily_special_sales']

        # 各種スコアの計算
        time_score = np.mean(time_scores)  # 時間帯スコアの平均
        sales_rate = (total_sales / total_prepared) * 100  # 総販売率
        early_sales_rate = (early_sales / total_prepared) * 100  # 前半販売率

        # 最終スコアの計算（時間帯重み60%、総販売率40%）
        final_score = (time_score * 0.6 + sales_rate * 0.4) / 100

        results.append({
            'date': date,
            'menu_name': menu_name,
            'prepared_amount': total_prepared,
            'total_sales': total_sales,
            'sales_rate': round(sales_rate, 2),
            'early_sales_rate': round(early_sales_rate, 2),
            'time_weighted_score': round(time_score, 2),
            'final_score': round(final_score, 2)
        })

    return pd.DataFrame(results)


def analyze_sales_pattern_simple(sales_data):
    """
    メニューごとの販売パターンを分類する関数（シンプル版）
    """
    patterns = {}

    for date in sales_data['date'].unique():
        menu_data = sales_data[sales_data['date'] == date]
        menu_name = menu_data.iloc[0]['menu_name']

        # 時間帯ごとの販売数を取得
        sales_pattern = menu_data['daily_special_sales'].tolist()

        # 各時間帯の販売比率を計算
        early_sales = sum(sales_pattern[:2])  # 前半（11:00-12:00）
        late_sales = sum(sales_pattern[2:])  # 後半（12:00-13:00）
        mid_peak = sales_pattern[1] + sales_pattern[2]  # 中間時間帯

        total_sales = sum(sales_pattern)
        if total_sales == 0:
            patterns[menu_name] = "データなし"
            continue

        # パターンの判定（販売比率で判断）
        if early_sales / total_sales > 0.45:
            pattern = "前半型（開店直後が人気）"
        elif mid_peak / total_sales > 0.45:
            pattern = "中間型（お昼時が人気）"
        else:
            pattern = "分散型（時間帯による偏りが少ない）"

        patterns[menu_name] = pattern

    return patterns


# メイン処理
if __name__ == "__main__":
    # CSVファイルの読み込み
    sales_data = pd.read_csv('sales_data.csv', encoding='utf-8')
    prepared_data = pd.read_csv('prepared_data.csv', encoding='utf-8')

    # 人気度分析の実行
    results = analyze_menu_popularity_simple(sales_data, prepared_data)

    # 結果の表示
    print("\n=== メニュー別人気度ランキング（スコア順）===")
    display_cols = ['menu_name', 'final_score', 'sales_rate', 'early_sales_rate']
    print(results.sort_values('final_score', ascending=False)[display_cols].to_string(index=False))

    # 販売パターンの分析と表示
    patterns = analyze_sales_pattern_simple(sales_data)
    print("\n=== 販売パターン分類 ===")
    for menu, pattern in patterns.items():
        print(f"{menu}: {pattern}")