# Hackathon2025Spring

## 概要
このプロジェクトは○○を目的としたWebアプリケーションです。

## デモ・スクリーンショット
（スクショ or デプロイURLがあれば）

## 使用技術
- Python 3.12.3
- Django 4.2
- HTML / CSS / JavaScript
- SQLite
- その他ライブラリ（ 例Bootstrap ）

## 機能一覧
- 開発しながら追記予定

## セットアップ手順（開発者向け）
WSL2のインストール  
wsl --install  
Windowsを再起動（これでUbuntuが使えるようになるらしい）  
VSCodeで拡張機能のWSLをインストール  
cmdを開きLinuxコマンドを実行  
wsl  
Ubuntuのアップデート、アップグレードを行う    
sudo apt update && sudo apt upgrade  
cat /etc/os-releaseでバージョンの確認ができる  
mkdirで任意のフォルダを作成  
cd で先ほど作成したフォルダに移動  
仮想環境を構築するためにvenvをインストール  
sudo apt install python3-venv  
仮想環境を作成するフォルダ名はvenvとする  
python3 -m venv venv  
VSCodeでwslに接続する  
任意のフォルダでリポジトリと連携する
git remote add origin git@github.com:nayutarou/Hackathon2025Spring.git
プルする
git pull origin main
作成した仮想環境を有効化する  
source venv/bin/activate  
Djangoのインストール  
pip install django==4.2  
