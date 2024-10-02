import copy
import tkinter as tk

class OthelloGame:
    def __init__(self, root):
        # rootオブジェクト
        self.root = root
        # ウィンドウのタイトル
        self.root.title("Othello Game")
        # 盤面サイズ
        self.board_size = 8
        # マス目の大きさ
        self.cell_size = 50
        # 軸ラベル用の余白
        self.margin = 30
        # ボードの状態（黒、白、None）
        self.board = [[None for _ in range(self.board_size)] for _ in range(self.board_size)]
        # 先行を黒に指定
        self.turn = "black"
        # 履歴を保存するためのリスト
        self.history = [] 
        self.create_sidebar()
        self.create_board()
        self.initialize_board()
        self.update_turn_display()
        self.update_score()
        self.highlight_valid_moves()

    def create_board(self):
        # Canvasの定義
        canvas_size = self.board_size * self.cell_size + 2 * self.margin
        self.canvas = tk.Canvas(self.root, width=canvas_size, height=canvas_size)
        # グリッドの作成
        self.canvas.grid(row=0, column=0)
        # グリッドの設定
        for i in range(self.board_size):
            for j in range(self.board_size):
                x0 = self.margin + i * self.cell_size
                y0 = self.margin + j * self.cell_size
                x1 = x0 + self.cell_size
                y1 = y0 + self.cell_size
                self.canvas.create_rectangle(x0, y0, x1, y1, outline="black", fill="green")
             
        # 横軸に数字（1-8）を表示
        for i in range(self.board_size):
            x = self.margin // 4 + (i + 1) * self.cell_size
            y = self.margin // 2
            self.canvas.create_text(x, y, text=str(i + 1), font=("Helvetica", 14))

        # 縦軸にアルファベット（A-H）を表示
        for j in range(self.board_size):
            x = self.margin // 2  # 左側マージンに配置
            y = self.margin // 4 + (j + 1) * self.cell_size
            self.canvas.create_text(x, y, text=chr(65 + j), font=("Helvetica", 14))    
            
        # クリックイベント（左ボタンクリック時に、handle_clickメソッドを呼び出す）
        self.canvas.bind("<Button-1>", self.handle_click)

    def initialize_board(self):
        # 初期盤面
        center = self.board_size // 2
        self.place_piece(center-1, center-1, "white")
        self.place_piece(center  , center  , "white")
        self.place_piece(center-1, center  , "black")
        self.place_piece(center  , center-1, "black")
        # 最初の状態を保存
        self.save_state()

    def save_state(self, move=None):
        # 現在の盤面と手番を履歴に保存
        self.history.append((copy.deepcopy(self.board), self.turn, move))
        if move:
            # move = (row, col, color) の形で保存されている
            row, col, color = move
            move_text = f"{color.capitalize()} : {chr(65+row)}{col+1}"
            self.history_listbox.insert(tk.END, move_text)  # リストに追加
            self.history_listbox.yview(tk.END)  # 最新の手を表示
    
    def undo_move(self):
        # 待った機能で1ターン戻る処理
        if len(self.history) > 1:
            self.history.pop()  # 現在の状態を削除して前の状態に戻す
            previous_state = self.history[-1]  # 前の履歴状態を取得
            self.board = copy.deepcopy(previous_state[0])  # 盤面を復元
            self.turn = previous_state[1]  # 手番を復元

            # 履歴リストからも最後の手を削除
            self.history_listbox.delete(tk.END)
            #self.board, self.turn, _ = self.history[-1]  # 前の状態を復元
            self.update_turn_display()
            self.redraw_board()  # 盤面を再描画
            self.update_score()
            self.highlight_valid_moves()
    
    def redraw_board(self):
        # ボードの状態を再描画する
        self.canvas.delete("piece")  # 駒を全て消す
        for row in range(self.board_size):
            for col in range(self.board_size):
                if self.board[row][col] is not None:
                    self.place_piece(row, col, self.board[row][col])

    def place_piece(self, row, col, color):
        x0 = self.margin + col * self.cell_size + self.cell_size // 4
        y0 = self.margin + row * self.cell_size + self.cell_size // 4
        x1 = self.margin + (col + 1) * self.cell_size - self.cell_size // 4
        y1 = self.margin + (row + 1) * self.cell_size - self.cell_size // 4
        # マスの状態を更新
        self.board[row][col] = color
        # 駒を描画
        self.canvas.create_oval(x0, y0, x1, y1, fill=color, tags="piece")

    def handle_click(self, event):
        # クリック位置からマスを判定
        col = (event.x - self.margin) // self.cell_size
        row = (event.y - self.margin) // self.cell_size
        
        # クリック位置が正しくない場合は、無効
        if not (0 <= row < self.board_size and 0 <= col < self.board_size):
            return
        
        # 合法手かどうか判定し、
        if self.is_valid_move(row, col, self.turn):
            # 駒を置く
            self.place_piece(row, col, self.turn)
            color = self.turn
            # 駒をひっくり返す
            self.flip_pieces(row, col)
            # スコアの更新
            self.update_score()
            # 手番の更新
            self.turn = "white" if self.turn == "black" else "black"
            # 新しい状態を保存
            self.save_state(move=(row, col, color))
            # 盤面を更新
            self.update_turn_display()
            # 駒を置けるマスをハイライト表示
            self.highlight_valid_moves()
            # 駒を置けるマスがなければ、パス
            if not self.has_valid_moves(self.turn):
                self.pass_turn()

    def is_valid_move(self, row, col, color):
        # 既に駒が置かれていれば、Falseを返す。
        if self.board[row][col] is not None:
            return False
        # 八方向（縦、横、斜め）
        directions = [(0, 1), (1, 0), (0, -1), (-1, 0), (1, 1), (-1, -1), (1, -1), (-1, 1)]
        # デフォルトをFalseに設定
        valid = False
        # 各方向のマスの状態を確認
        for direction in directions:
            if self.check_direction(row, col, direction, color):
                valid = True
        return valid

    def check_direction(self, row, col, direction, color):
        # 相手の駒の色を代入
        opponent_color = "white" if color == "black" else "black"
        # 指定の方向のマスを確認
        d_row, d_col = direction
        row += d_row
        col += d_col
        # 盤面外であれば、Falseを返す
        if not (0 <= row < self.board_size and 0 <= col < self.board_size):
            return False
        # 相手の駒がなければ、Falseを返す
        if self.board[row][col] != opponent_color:
            return False
        while 0 <= row < self.board_size and 0 <= col < self.board_size:
            # マスがNoneであれば、Falseを返す
            if self.board[row][col] is None:
                return False
            # 自分の駒があれば、Trueを返す
            if self.board[row][col] == color:
                return True
            row += d_row
            col += d_col
        return False

    def flip_pieces(self, row, col):
        directions = [(0, 1), (1, 0), (0, -1), (-1, 0), (1, 1), (-1, -1), (1, -1), (-1, 1)]
        for direction in directions:
            if self.check_direction(row, col, direction, self.turn):
                self.flip_in_direction(row, col, direction)

    def flip_in_direction(self, row, col, direction):
        opponent_color = "white" if self.turn == "black" else "black"
        d_row, d_col = direction
        row += d_row
        col += d_col
        while self.board[row][col] == opponent_color:
            # 相手の駒を自分の駒に置き換える
            self.place_piece(row, col, self.turn)
            row += d_row
            col += d_col

    def highlight_valid_moves(self):
        # 前の盤面でのハイライトを削除
        self.canvas.delete("highlight")
        has_moves = False
        for row in range(self.board_size):
            for col in range(self.board_size):
                if self.is_valid_move(row, col, self.turn):
                    has_moves = True
                    x0 = self.margin + col * self.cell_size + self.cell_size // 2 - 5
                    y0 = self.margin + row * self.cell_size + self.cell_size // 2 - 5
                    x1 = self.margin + col * self.cell_size + self.cell_size // 2 + 5
                    y1 = self.margin + row * self.cell_size + self.cell_size // 2 + 5
                    self.canvas.create_oval(x0, y0, x1, y1, fill="gray", tags="highlight")
        if not has_moves:
            print(f"{self.turn.capitalize()} has no valid moves")

    def has_valid_moves(self, color):
        for row in range(self.board_size):
            for col in range(self.board_size):
                if self.is_valid_move(row, col, color):
                    return True
        return False

    def pass_turn(self):
        # パスしたら次のプレイヤーに手番を渡す
        self.turn = "white" if self.turn == "black" else "black"
        self.update_turn_display()
        self.highlight_valid_moves()

        # 次のプレイヤーにも合法手がない場合、ゲームを終了する
        if not self.has_valid_moves(self.turn):
            self.end_game()

    def end_game(self):
        black_count, white_count = self.count_pieces()
        if black_count > white_count:
            winner = "黒の勝利！"
        elif white_count > black_count:
            winner = "白の勝利！"
        else:
            winner = "引き分け！"

        self.canvas.create_text(
            self.board_size * self.cell_size // 2 + self.margin,
            self.board_size * self.cell_size // 2 + self.margin,
            text=f"{winner}",
            font=("Helvetica", 36),
            fill="red"
        )

    def create_sidebar(self):
        self.sidebar = tk.Frame(self.root)
        self.sidebar.grid(row=0, column=1, sticky="ns")

        self.turn_player_label = tk.Label(self.sidebar, text="Turn Player: Black", font=("Helvetica", 14))
        self.turn_player_label.pack(pady=10)

        self.turn_label = tk.Label(self.sidebar, text="Turn: 1", font=("Helvetica", 14))
        self.turn_label.pack(pady=10)

        self.score_label = tk.Label(self.sidebar, text="", font=("Helvetica", 14))
        self.score_label.pack(pady=10)
        
        # undoボタン
        self.undo_button = tk.Button(self.sidebar, text="Undo", command=self.undo_move, font=("Helvetica", 14))
        self.undo_button.pack(pady=10)

        # スクロールバー付きの履歴リストを作成
        self.scrollbar = tk.Scrollbar(self.sidebar)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.history_listbox = tk.Listbox(self.sidebar, yscrollcommand=self.scrollbar.set, font=("Helvetica", 12), height=10)
        self.history_listbox.pack(pady=10, fill=tk.BOTH)
        self.scrollbar.config(command=self.history_listbox.yview)

    def update_turn_display(self):
        self.turn_player_label.config(text=f"Turn Player: {self.turn.capitalize()}")
        self.turn_label.config(text=f"Turn: {len(self.history)}")

    def update_score(self):
        black_count, white_count = self.count_pieces()
        self.score_label.config(text=f"Black: {black_count}  White: {white_count}")

    def count_pieces(self):
        black_count = 0
        white_count = 0
        for row in range(self.board_size):
            for col in range(self.board_size):
                if self.board[row][col] == "black":
                    black_count += 1
                elif self.board[row][col] == "white":
                    white_count += 1
        return black_count, white_count

if __name__ == "__main__":
    root = tk.Tk()
    game = OthelloGame(root)
    root.mainloop()