#!/usr/bin/env python3
"""
验证MCP和Skill集成
"""
import requests
import time
import sys
import os

def check_api_health():
    """检查API健康状态"""
    try:
        response = requests.get("http://localhost:8000/health")
        return response.status_code == 200
    except requests.exceptions.ConnectionError:
        return False

def list_skills():
    """列出所有技能"""
    try:
        response = requests.get("http://localhost:8000/api/v1/skills")
        if response.status_code == 200:
            skills = response.json().get("skills", [])
            return skills
        return []
    except requests.exceptions.ConnectionError:
        return []

def main():
    print("🔍 验证MCP和Skill集成...")
    
    # 检查API是否运行
    print("📡 检查API服务...")
    if not check_api_health():
        print("❌ API服务未运行")
        return
    
    print("✅ API服务运行正常")
    
    # 等待服务完全启动
    time.sleep(2)
    
    # 列出技能
    print("📋 获取已注册技能...")
    skills = list_skills()
    
    if skills:
        print(f"✅ 找到 {len(skills)} 个技能:")
        for skill in skills:
            print(f"  - {skill['name']}: {skill['description']}")
    else:
        print("❌ 未找到任何技能")
        return
    
    print("\n🎉 验证完成！MCP和Skill集成正常工作。")

if __name__ == "__main__":
    main()