import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
import json
import os

BACKGROUND = "back.png"
TEMPLATE_FILE = "template.json"

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("画像合成アプリ")

        CANVAS_W, CANVAS_H = 1200, 800
        self.canvas = tk.Canvas(root, width=CANVAS_W, height=CANVAS_H)
        self.canvas.pack()

        # 背景画像読み込み
        self.bg_img_original = Image.open(BACKGROUND)
        self.bg_img = self.bg_img_original.resize((CANVAS_W, CANVAS_H), Image.LANCZOS)
        self.bg_tk = ImageTk.PhotoImage(self.bg_img)

        # 背景は1回だけ描画し、タグを付ける
        self.bg_item = self.canvas.create_image(0, 0, anchor="nw", image=self.bg_tk, tags="background")

        # テンプレート(JSONファイル)を読み込む
        if os.path.exists(TEMPLATE_FILE):
            with open(TEMPLATE_FILE) as f:
                data = json.load(f)
            self.positions = data["positions"]
            print("テンプレート読み込み:", self.positions)
        else:
            self.positions = []  # 手動配置用
            print("テンプレートなし → 手動配置モード")

        self.current_index = 0
        self.thumb_size = (90, 150)

        # アプリの画面下に表示されるボタン群
        tk.Button(root, text="画像を追加", command=self.load_image).pack()
        tk.Button(root, text="位置テンプレート保存", command=self.save_template).pack()
        tk.Button(root, text="合成画像保存", command=self.save_image).pack()

        self.user_images = []
        self.user_thumbs = []
        self.drag_target = None

        # ドラッグ操作
        self.canvas.bind("<ButtonPress-1>", self.start_drag)
        self.canvas.bind("<B1-Motion>", self.dragging)
        self.canvas.bind("<ButtonRelease-1>", self.end_drag)

    # 画像追加
    def load_image(self):
        file = filedialog.askopenfilename()
        if not file:
            return

        img = Image.open(file)
        self.user_images.append(img)

        thumb = img.resize(self.thumb_size, Image.LANCZOS)
        thumb_tk = ImageTk.PhotoImage(thumb)
        self.user_thumbs.append(thumb_tk)

        if self.positions:
            # テンプレート位置に自動配置
            if self.current_index >= len(self.positions):
                print("テンプレートの位置が足りません")
                return
            x, y = self.positions[self.current_index]
        else:
            # 手動配置モード：中央に仮置き
            x, y = 300, 200

        item = self.canvas.create_image(x, y, anchor="nw", image=thumb_tk)
        self.current_index += 1
 
    # ドラッグ開始
    def start_drag(self, event):
        item = self.canvas.find_closest(event.x, event.y)
        if item:
            # 背景はドラッグ対象にしない
            if "background" in self.canvas.gettags(item[0]):
                return
            self.drag_target = item[0]

    # ドラッグ中
    def dragging(self, event):
        if self.drag_target:
            self.canvas.coords(self.drag_target, event.x, event.y)

    # ドラッグ終了
    def end_drag(self, event):
        self.drag_target = None

    # 位置テンプレート保存
    def save_template(self):
        items = self.canvas.find_all()
        positions = []

        # 背景画像 item[0] を除外
        for item in items[1:]:
            x, y = self.canvas.coords(item)
            positions.append([int(x), int(y)])

        with open(TEMPLATE_FILE, "w") as f:
            json.dump({"positions": positions}, f, indent=2)

        print("テンプレート保存:", positions)

    # 合成画像保存
    def save_image(self):
        result = self.bg_img_original.copy()

        for i, img in enumerate(self.user_images):
            if i < len(self.positions):
                x, y = self.positions[i]
                result.paste(img.resize(self.thumb_size, Image.LANCZOS), (x, y))

        result.save("output.png")
        print("保存しました：output.png")

root = tk.Tk()
App(root)
root.mainloop()