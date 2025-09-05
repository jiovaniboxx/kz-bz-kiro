"use client";

import React, { useState } from "react";
import {
  Avatar,
  Box,
  Button,
  Checkbox,
  FormControlLabel,
  Grid,
  Link,
  Modal,
  Paper,
  TextField,
  Typography
} from "@mui/material";
import LockOutlinedIcon from "@mui/icons-material/LockOutlined";
import { teal } from "@mui/material/colors";
import axios from "axios";

const SigninModal = ({ open, handleClose }: { open: boolean; handleClose: () => void }) => {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSignin = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      const res = await axios.post("/api/auth/signin", { email, password });
      // 認証成功時の処理（例: トークン保存や画面遷移など）
      alert("サインイン成功");
      handleClose();
    } catch (err) {
      alert("サインイン失敗");
    } finally {
      setLoading(false);
    }
  };

  return (
    <Modal
      open={open}
      onClose={handleClose}
      sx={{
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
      }}
    >
      <Paper
        elevation={3}
        sx={{
          p: 4,
          width: "300px",
          maxWidth: "90%", // モバイル対応
          m: "auto",
          textAlign: "center", // 中央揃え
        }}
      >
        <form onSubmit={handleSignin}>
          <Grid
            container
            direction="column"
            justifyContent="flex-start"
            alignItems="center"
          >
            <Avatar sx={{ bgcolor: teal[400], mb: 2 }}>
              <LockOutlinedIcon />
            </Avatar>
            <Typography variant="h5" sx={{ mb: 3 }}>
              Sign In
            </Typography>
          </Grid>
          <TextField
            label="e-mail"
            variant="standard"
            fullWidth
            required
            sx={{ mb: 2 }}
            value={email}
            onChange={e => setEmail(e.target.value)}
          />
          <TextField
            type="password"
            label="Password"
            variant="standard"
            fullWidth
            required
            sx={{ mb: 2 }}
            value={password}
            onChange={e => setPassword(e.target.value)}
          />
          <FormControlLabel
            labelPlacement="end"
            label="パスワードを忘れました"
            control={<Checkbox name="checkboxA" size="small" color="primary" />}
            sx={{ mb: 2 }}
          />
          <Box mt={3}>
            <Button
              type="submit"
              color="primary"
              variant="contained"
              fullWidth
              disabled={loading}
            >
              サインイン
            </Button>
            <Typography variant="caption" mt={2}>
              <Link href="#">パスワードを忘れましたか？</Link>
            </Typography>
          </Box>
        </form>
      </Paper>
    </Modal>
  );
};

export default SigninModal;
