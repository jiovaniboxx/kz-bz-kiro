"use client";

import React from "react";
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

const SigninModal = ({ open, handleClose }: { open: boolean; handleClose: () => void }) => {
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
        <TextField label="e-mail" variant="standard" fullWidth required sx={{ mb: 2 }} />
        <TextField
          type="password"
          label="Password"
          variant="standard"
          fullWidth
          required
          sx={{ mb: 2 }}
        />
        <FormControlLabel
          labelPlacement="end"
          label="パスワードを忘れました"
          control={<Checkbox name="checkboxA" size="small" color="primary" />}
          sx={{ mb: 2 }}
        />
        <Box mt={3}>
          <Button type="submit" color="primary" variant="contained" fullWidth>
            サインイン
          </Button>
          <Typography variant="caption" mt={2}>
            <Link href="#">パスワードを忘れましたか？</Link>
          </Typography>
          {/* <Typography variant="caption" display="block" mt={1}>
            アカウントを持っていますか？
            <Link href="/">
              アカウントを作成
            </Link>
          </Typography> */}
        </Box>
      </Paper>
    </Modal>
  );
};

export default SigninModal;
