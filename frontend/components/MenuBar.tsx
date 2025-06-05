"use client";

import React, { useState } from "react";
import Link from "next/link";
import { AppBar, Toolbar, Typography, Button, Box } from "@mui/material";
import SigninModal from "./Signin"; // 修正: Signin を SigninModal に変更
import Signup from "./Signup"; // Signupコンポーネントをインポート
import styles from "../styles/menubar.module.css"; // CSSモジュールをインポート

interface MenuBarProps {
  className?: string;
}

const MenuBar: React.FC<MenuBarProps> = ({ className }) => {
  const [openLogin, setOpenLogin] = useState(false); // ログインモーダルの開閉状態
  const [openSignup, setOpenSignup] = useState(false); // サインアップモーダルの開閉状態

  const handleOpenLogin = () => setOpenLogin(true);
  const handleCloseLogin = () => setOpenLogin(false);

  const handleOpenSignup = () => setOpenSignup(true);
  const handleCloseSignup = () => setOpenSignup(false);

  return (
    <>
      <AppBar position="static" className={`${styles.navbar} ${className}`} sx={{ backgroundColor: "#ffffff" }}>
        <Toolbar className={styles.toolbar}>
          <Typography variant="h6" className={styles.title}>
            <Link href="/" className={styles.menuItem}>
              ビバリーママのENGLISHカフェ
            </Link>
          </Typography>
          <Box
            className={styles.menuItems}
            sx={{
              display: "flex",
              justifyContent: "center",
              alignItems: "center",
              flexGrow: 1,
            }}
          >
            <Button color="inherit" component={Link} href="/" className={styles.menuItem} sx={{ color: "black" }}>
              ホーム
            </Button>
            <Button color="inherit" component={Link} href="/news" className={styles.menuItem} sx={{ color: "black" }}>
              お知らせ
            </Button>
            <Button color="inherit" component={Link} href="/lessons" className={styles.menuItem} sx={{ color: "black" }}>
              レッスン
            </Button>
            <Button color="inherit" component={Link} href="/concept" className={styles.menuItem} sx={{ color: "black" }}>
              コンセプト
            </Button>
            <Button color="inherit" component={Link} href="/pricing" className={styles.menuItem} sx={{ color: "black" }}>
              料金
            </Button>
            <Button color="inherit" component={Link} href="/contact" className={styles.menuItem} sx={{ color: "black" }}>
              お問い合わせ
            </Button>
          </Box>
          {/* サインインとサインアップボタンを並べる */}
          <Box sx={{ display: "flex", gap: 2, alignItems: "center", marginLeft: "auto" }}>
            <Button
              onClick={handleOpenSignup} // サインアップモーダルを開く
              className={styles.signupButton}
              sx={{
                backgroundColor: "#007BFF", // 青色
                color: "white", // 白文字
                "&:hover": {
                  backgroundColor: "#0056b3", // ホバー時の色
                },
              }}
            >
              ユーザー登録
            </Button>
            <Button
              onClick={handleOpenLogin} // ログインモーダルを開く
              className={styles.signupButton}
              sx={{
                backgroundColor: "#FF0000", // 赤色
                color: "white", // 白文字
                "&:hover": {
                  backgroundColor: "#CC0000", // ホバー時の色
                },
              }}
            >
              ログイン
            </Button>
          </Box>
        </Toolbar>
      </AppBar>

      {/* ログインモーダル */}
      <SigninModal open={openLogin} handleClose={handleCloseLogin} />

      {/* サインアップモーダル */}
      <Signup open={openSignup} handleClose={handleCloseSignup} />
    </>
  );
};

export default MenuBar;