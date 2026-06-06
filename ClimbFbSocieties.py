import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service

def scrape_fb_group_members():
    print("🚀 正在啟動 Chrome 瀏覽器...")
    
    # 初始化 WebDriver
    options = webdriver.ChromeOptions()
    # 關閉自動化測試通知列，減少被臉書偵測的機率
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    
    driver = webdriver.Chrome(options=options)
    
    try:
        # 1. 導航至臉書首頁
        driver.get("https://www.facebook.com/")
        
        print("\n==================================================")
        print("💡 【請執行人工操作】：")
        print("1. 請在開啟的瀏覽器中登入您的 Facebook 帳號。")
        print("2. 登入後，手動切換到您要爬取的「社團成員頁面」。")
        print("==================================================")
        
        input("\n確認瀏覽器已停在【社團成員頁面】後，請回這裡按下 [Enter] 開始全自動爬取...")
        print("\n🤖 腳本開始執行，請勿關閉瀏覽器視窗...")

        members_data = []
        seen_urls = set()  # 用於動態去重（臉書個人網址是唯一值）
        
        last_height = driver.execute_script("return document.body.scrollHeight")
        no_new_member_count = 0  # 紀錄連續幾次滾動沒有新資料
        scroll_times = 0

        while True:
            # 2. 抓取當前畫面上的所有成員連結
            # 專家心法：臉書的成員名字一定會包裹在含有 "/user/" 的 <a> 標籤內
            member_elements = driver.find_elements(By.CSS_SELECTOR, 'a[href*="/user/"]')
            
            new_found_this_turn = False
            
            for elem in member_elements:
                try:
                    name = elem.text.strip()
                    url = elem.get_attribute('href')
                    
                    # 清理網址，去掉後面帶有的 ?fref=... 等追蹤參數，還原純淨的個人網址
                    if url and '?' in url:
                        url = url.split('?')[0]
                        
                    # 只有當「名字不為空」且「網址沒抓過」時才寫入，防止虛擬列表漏抓
                    if name and url and url not in seen_urls:
                        seen_urls.add(url)
                        members_data.append({
                            'FB名稱': name,
                            '個人網址': url
                        })
                        print(f"✨ [已抓取] {name}")
                        new_found_this_turn = True
                except Exception:
                    # 忽略滾動過程中因網頁動態更新而自然失效的元素
                    continue
            
            # 3. 執行向下滾動
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            scroll_times += 1
            time.sleep(2)  # 每隔 2 秒滾動一次，符合臉書安全速限
            
            # 4. 檢查是否到達底部
            new_height = driver.execute_script("return document.body.scrollHeight")
            
            if new_found_this_turn:
                no_new_member_count = 0
            else:
                no_new_member_count += 1
                
            # 判定結束條件：如果頁面高度連續 5 次沒有變化，且這 5 次都沒有新成員入帳，代表真的滾到底了
            if new_height == last_height and no_new_member_count >= 5:
                print("\n🏁 已成功到達頁面底部，且無新成員加入。")
                break
                
            last_height = new_height
            
            # 每滾動 10 次在終端機回報一次進度
            if scroll_times % 10 == 0:
                print(f"📊 目前進度：已累計抓取 {len(members_data)} 位成員...")

        # 5. 轉換成資料表並匯出 Excel
        print("\n💾 正在產生 Excel 檔案...")
        df = pd.DataFrame(members_data)
        
        # 確保有名單才匯出
        if not df.empty:
            output_filename = "FB社團成員名單_生鮮自動抓取.xlsx"
            df.to_excel(output_filename, index=False)
            print(f"🎉 任務完成！總共抓取了 {len(members_data)} 位成員。")
            print(f"檔案已儲存至：{output_filename}")
        else:
            print("❌ 爬取結束，但未成功抓取到任何成員資料，請檢查選擇器或社團頁面結構。")

    except Exception as e:
        print(f"💥 程式執行發生錯誤: {e}")
        
    finally:
        # 關閉瀏覽器
        driver.quit()
        print("👋 瀏覽器已關閉。")

if __name__ == "__main__":
    scrape_fb_group_members()