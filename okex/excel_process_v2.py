import os
import pandas as pd
from openai import OpenAI
from dotenv import load_dotenv
import time

# 加载环境变量
load_dotenv()

# 新增配置参数
CONFIG = {
    "retry_delay": 5,  # 失败重试延迟（秒）
    "max_retries": 5,  # 最大重试次数
    "output_suffix": "_analysis.txt"  # 结果文件后缀
}


def analyze_data_with_deepseek(data_summary, prompt_template):
    """
    使用DeepSeek API分析数据
    """
    client = OpenAI(api_key="sk-0f0b92504f7244daa75870008d1092e1", base_url="https://api.deepseek.com")

    full_prompt = f"{prompt_template}\n\n数据摘要：\n{data_summary}"

    try:
        response = client.chat.completions.create(
            model="deepseek-reasoner",  # DeepSeek专用模型
            messages=[
                {"role": "user", "content": full_prompt}
            ],
            temperature=0.7,
            frequency_penalty=0.3  # 推荐参数
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"DeepSeek API调用失败: {str(e)}")
        return None


def process_excel_file(file_path, output_folder, prompt_template):
    """
    处理单个Excel文件（增加重试机制）
    """
    retries = 0
    output_filename = f"{os.path.splitext(os.path.basename(file_path))[0]}{CONFIG['output_suffix']}"
    output_path = os.path.join(output_folder, output_filename)

    while retries <= CONFIG['max_retries']:
        try:
            df = pd.read_excel(file_path, sheet_name=0)
            data_summary = f"""
            文件: {os.path.basename(file_path)}
            行数: {len(df)}
            列数: {len(df.columns)}
            前3行样例数据:
            {df.head(3).to_csv(index=False)}
            """

            analysis_result = analyze_data_with_deepseek(data_summary, prompt_template)

            if analysis_result:
                with open(output_path, "w", encoding="utf-8") as f:
                    f.write(f"DeepSeek分析报告 - {os.path.basename(file_path)}\n")
                    f.write(f"生成时间: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                    f.write(analysis_result)

                print(f"分析结果已保存至: {output_path}")
                return True
            else:
                print(f"文件分析失败: {file_path}")
                return False

        except Exception as e:
            if retries < CONFIG['max_retries']:
                print(f"分析失败（{retries + 1}/{CONFIG['max_retries']}），5秒后重试... 错误信息：{str(e)}")
                time.sleep(CONFIG['retry_delay'])
                retries += 1
            else:
                print(f"达到最大重试次数{CONFIG['max_retries']}次，跳过文件: {file_path}")
                return False


def analyze_excel_files(input_folder, output_folder, prompt_template):
    """
    遍历处理Excel文件（增加去重逻辑）
    """
    os.makedirs(output_folder, exist_ok=True)

    processed_files = {
        os.path.splitext(f)[0]
        for f in os.listdir(output_folder)
        if f.endswith(CONFIG['output_suffix'])
    }

    for filename in os.listdir(input_folder):
        if filename.endswith((".xlsx", ".xls")) and not filename.startswith("~$"):
            # 去重检查
            base_name = os.path.splitext(filename)[0]
            if base_name in processed_files:
                print(f"跳过已分析文件: {filename}")
                continue

            file_path = os.path.join(input_folder, filename)
            print(f"\n正在处理文件: {filename}")

            if process_excel_file(file_path, output_folder, prompt_template):
                processed_files.add(base_name)

            time.sleep(1.2)


if __name__ == "__main__":
    INPUT_FOLDER = "D:/deepseek/"
    OUTPUT_FOLDER = "D:/deepseek/"

    ANALYSIS_PROMPT = """请分别分析表中1.以D列供应商为基础，对E至I列进行汇总
2.分级：
①I列汇总金额高于5000万的，或H列汇总金额高于8000万的作为极高风险供应商（4级）；
②I列汇总金额介于100万-5000万，或H列汇总金额介于3000万-8000万，作为高风险供应商（3级）
③I列汇总金额小于100万，或H列汇总金额介于1000万-3000万，作为中度风险供应商（2级）
④其他情况作为低风险供应商（1级）
3.输出：
①供应商评级清单：第一列为供应商编码，第二列为供应商评级，如1级
②按金额乘以供应商级数汇总得到这个区域的风险等级：第一列为区域名称，第二列为区域风险等级计算结果。 
    一、供应商情况总结
    现状：
    风险：
    建议：
    二、账龄情况总结
    现状：
    风险：
    建议：
    三、区域维度供应商风险总结
    现状：
    风险：
    建议：
    四、风险控制：
    短期：
    中期：
    长期：
    五、老板一句话总结："""

    # 执行分析
    analyze_excel_files(INPUT_FOLDER, OUTPUT_FOLDER, ANALYSIS_PROMPT)
