import React from 'react';
import { Container, Box } from '@mui/material';
import Home from "../components/Home";
import Slideshow from "../components/Slideshow";
import styles from './page.module.css'; // CSSモジュールをインポート

export default function Page() {
  return (
    <div className={styles.pageContainer}>
      <Box className={styles.slideshowContainer}>
        <Slideshow />
      </Box>
      <Container maxWidth="lg" className={styles.homeContainer}>
        <Home />
      </Container>
    </div>
  );
}