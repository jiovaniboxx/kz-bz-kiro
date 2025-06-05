"use client";
import React, { useState, useEffect } from 'react';
import { Box } from '@mui/material';
import { CldImage } from 'next-cloudinary';
import styles from '../styles/Slideshow.module.css';

const images = [
  "samples/animals/cat",
  "samples/two-ladies",
  "cld-sample",
  "samples/smile",
  "cld-sample-3",
  "cld-sample-4",
  "cld-sample-5",
  "samples/man-portrait",
  "samples/balloons",
  "samples/upscale-face-1",
];

const Slideshow: React.FC = () => {
  const [currentImageIndex, setCurrentImageIndex] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentImageIndex((prevIndex) => (prevIndex + 1) % images.length);
    }, 3000);

    return () => clearInterval(interval);
  }, []);

  return (
    <Box className={styles.slideshow}>
      <CldImage
        src={images[currentImageIndex]}
        width="1920"
        height="1080"
        crop="fill"
        alt="Slideshow Image"
        className={styles.image}
      />
    </Box>
  );
};

export default Slideshow;