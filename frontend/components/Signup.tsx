"use client";

import React, { useState } from "react";
import {
  Avatar,
  Box,
  Button,
  Checkbox,
  FormControl,
  FormControlLabel,
  Grid,
  InputLabel,
  Link,
  MenuItem,
  Modal,
  Paper,
  Select,
  TextField,
  Typography
} from "@mui/material";
import PersonAddIcon from "@mui/icons-material/PersonAdd";
import { teal } from "@mui/material/colors";
import SigninModal from "./Signin"; // 修正: Signin を SigninModal に変更
import axios from "axios";

const SignupModal = ({ open, handleClose }: { open: boolean; handleClose: () => void }) => {
  const [postalCode, setPostalCode] = useState("");
  const [address, setAddress] = useState("");
  const [age, setAge] = useState("");
  const [openSignin, setOpenSignin] = useState(false);

  const toHalfWidth = (str: string) => {
    return str.replace(/[Ａ-Ｚａ-ｚ０-９]/g, (s) =>
      String.fromCharCode(s.charCodeAt(0) - 0xfee0)
    );
  };

  const fetchAddress = async () => {
    const normalizedPostalCode = toHalfWidth(postalCode);
    if (normalizedPostalCode.length === 7) {
      try {
        const response = await axios.get(
          `https://zipcloud.ibsnet.co.jp/api/search?zipcode=${normalizedPostalCode}`
        );
        const result = response.data.results;
        if (result) {
          const fullAddress = `${result[0].address1}${result[0].address2}${result[0].address3}`;
          setAddress(fullAddress);
        } else {
          alert("該当する住所が見つかりませんでした。");
        }
      } catch (error) {
        console.error("住所の取得に失敗しました:", error);
        alert("住所の取得に失敗しました。");
      }
    }
  };

  const handleOpenSignin = () => {
    setOpenSignin(true);
    handleClose();
  };

  const handleCloseSignin = () => {
    setOpenSignin(false);
  };

  return (
    <>
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
            maxWidth: "90%",
            m: "auto",
            textAlign: "center",
          }}
        >
          <Grid
            container
            direction="column"
            justifyContent="flex-start"
            alignItems="center"
          >
            <Avatar sx={{ bgcolor: teal[400], mb: 2 }}>
              <PersonAddIcon />
            </Avatar>
            <Typography variant="h5" sx={{ mb: 3 }}>
              Sign Up
            </Typography>
          </Grid>
          <TextField
            label="郵便番号(ハイフンなし)"
            variant="standard"
            fullWidth
            required
            value={postalCode}
            onChange={(e) => setPostalCode(toHalfWidth(e.target.value))}
            onBlur={fetchAddress}
            sx={{ mb: 2 }}
          />
          <TextField
            label="住所"
            variant="standard"
            fullWidth
            required
            value={address}
            onChange={(e) => setAddress(e.target.value)}
            sx={{ mb: 2 }}
          />
          <FormControl fullWidth sx={{ mb: 2 }}>
            <InputLabel id="age-select-label">年齢</InputLabel>
            <Select
              labelId="age-select-label"
              value={age}
              onChange={(e) => setAge(e.target.value)}
              variant="standard"
            >
              {[...Array(100).keys()].map((num) => (
                <MenuItem key={num + 1} value={num + 1}>
                  {num + 1}歳
                </MenuItem>
              ))}
            </Select>
          </FormControl>
          <TextField label="レッスンの目的" variant="standard" fullWidth required sx={{ mb: 2 }} />
          <FormControlLabel
            labelPlacement="end"
            label={
              <>
                利用規約に同意します
                <Link href="/terms" target="_blank" style={{ marginLeft: "5px" }}>
                  (利用規約を読む)
                </Link>
              </>
            }
            control={<Checkbox name="terms" size="small" color="primary" />}
            sx={{ mb: 2 }}
          />
          <Box mt={3}>
            <Button type="submit" color="primary" variant="contained" fullWidth>
              アカウント作成
            </Button>
            <Typography variant="caption" mt={2}>
              すでにアカウントをお持ちですか？
              <Link onClick={handleOpenSignin} style={{ cursor: "pointer" }}>
                ログイン
              </Link>
            </Typography>
          </Box>
        </Paper>
      </Modal>

      <SigninModal open={openSignin} handleClose={handleCloseSignin} />
    </>
  );
};

export default SignupModal;