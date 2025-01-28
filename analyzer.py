import pandas as pd
import numpy as np


def analyze_menu_popularity(sales_data, prepared_data):
    """
    日替わりメニューの人気度を分析する関数

    Parameters:
    sales_data: 販売データのDataFrame（時間帯ごとの販売数）
    prepared_data: 作成数データのDataFrame（日ごとの作成数）
    """

    # 時間帯ごとの重み付け（早い時間帯の販売をより重視）
    time_weights = {
        '11:00-11:30': 2.0,  # オープン直後は2倍重視
        '11:30-12:00': 1.5,  # 2番目の時間帯は1.5倍
        '12:00-12:30': 1.0,  # 通常の重み
        '12:30-13:00': 0.5  # 最後の時間帯は半分の重み
    }

    # 分析結果を格納するリスト
    results = []

    # 日付ごとに分析を行う
    for date in sales_data['date'].unique():
        # その日のデータを抽出
        menu_data = sales_data[sales_data['date'] == date]
        prepared = prepared_data[prepared_data['date'] == date].iloc[0]

        # メニュー名と作成数を取得
        menu_name = prepared['menu_name']
        total_prepared = prepared['prepared_amount']

        # 時間帯ごとのスコアを計算
        time_scores = []  # 時間帯別スコアを格納するリスト
        early_sales = 0  # 前半（11:00-12:00）の販売数
        total_sales = 0  # 総販売数

        # 各時間帯のデータを処理
        for idx, row in menu_data.iterrows():
            # その時間帯での日替わりメニューのシェアを計算
            # 例）日替わり30個/全体75個 = 40%
            share = row['daily_special_sales'] / row['total_sales'] * 100

            # シェアに時間帯の重みを掛ける
            # 例）40% × 2.0 = 80点（11:00-11:30の場合）
            weighted_score = share * time_weights[row['time_slot']]
            time_scores.append(weighted_score)

            # 前半（11:00-12:00）の販売数を集計
            if row['time_slot'] in ['11:00-11:30', '11:30-12:00']:
                early_sales += row['daily_special_sales']

            # 総販売数を集計
            total_sales += row['daily_special_sales']

        # 各種スコアの計算
        time_score = np.mean(time_scores)  # 時間帯スコアの平均
        sales_rate = (total_sales / total_prepared) * 100  # 総販売率
        early_sales_rate = (early_sales / total_prepared) * 100  # 前半販売率

        # 最終スコアの計算（時間帯シェア60%、総販売率40%）
        final_score = (time_score * 0.6 + sales_rate * 0.4) / 100

        # 結果を辞書形式で保存
        results.append({
            'date': date,
            'menu_name': menu_name,
            'prepared_amount': total_prepared,  # 作成数
            'total_sales': total_sales,  # 総販売数
            'sales_rate': round(sales_rate, 2),  # 総販売率
            'early_sales_rate': round(early_sales_rate, 2),  # 前半販売率
            'time_weighted_score': round(time_score, 2),  # 時間帯スコア
            'final_score': round(final_score, 2)  # 最終スコア
        })

    # 結果をDataFrame形式で返す
    return pd.DataFrame(results)


# 販売パターンを分析する関数
def analyze_sales_pattern(sales_data):
    """
    メニューごとの販売パターンを分類する関数
    """
    patterns = {}

    # 日付ごとに販売パターンを分析
    for date in sales_data['date'].unique():
        menu_data = sales_data[sales_data['date'] == date]
        menu_name = menu_data.iloc[0]['menu_name']

        # 時間帯ごとの販売数をリストにする
        sales_pattern = []
        for _, row in menu_data.iterrows():
            sales_pattern.append(row['daily_special_sales'])

        # 各時間帯の販売数を比較
        early_sales = sum(sales_pattern[:2])  # 前半（11:00-12:00）
        late_sales = sum(sales_pattern[2:])  # 後半（12:00-13:00）
        mid_peak = sales_pattern[1] + sales_pattern[2]  # 中間時間帯

        # パターンの判定
        if early_sales > late_sales and early_sales > mid_peak:
            pattern = "早い時間帯重視"
        elif mid_peak > early_sales and mid_peak > late_sales:
            pattern = "お昼時重視"
        else:
            pattern = "後半に強い"

        patterns[menu_name] = pattern

    return patterns


# メイン処理
if __name__ == "__main__":
    # CSVファイルの読み込み
    sales_data = pd.read_csv('sales_data.csv')
    prepared_data = pd.read_csv('prepared_data.csv')

    # 人気度分析の実行
    results = analyze_menu_popularity(sales_data, prepared_data)

    # 結果の表示
    print("=== メニュー別人気度ランキング（スコア順）===")
    print(results.sort_values('final_score', ascending=False)[
              ['menu_name', 'final_score', 'sales_rate', 'early_sales_rate']
          ].to_string(index=False))

    # 販売パターンの分析と表示
    patterns = analyze_sales_pattern(sales_data)
    print("\n=== 販売パターン分類 ===")
    for menu, pattern in patterns.items():
        print(f"{menu}: {pattern}")