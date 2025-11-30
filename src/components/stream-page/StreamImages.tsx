import { useState } from 'react';
import {
  Box,
  Typography,
  ImageList,
  ImageListItem,
  Dialog,
  DialogContent,
  IconButton,
  useTheme,
  useMediaQuery,
} from '@mui/material';
import { Close } from '@mui/icons-material';
import { StreamImage } from '../../types/streamContent';

interface StreamImagesProps {
  images: StreamImage[];
}

export function StreamImages({ images }: StreamImagesProps) {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));
  const [selectedImage, setSelectedImage] = useState<StreamImage | null>(null);

  return (
    <Box sx={{ mb: 4 }}>
      <Typography
        variant="h6"
        sx={{
          mb: 2,
          fontWeight: 600,
          color: theme.palette.text.primary,
          borderBottom: `2px solid ${theme.palette.primary.main}`,
          pb: 1,
          display: 'inline-block',
        }}
      >
        Images
      </Typography>
      <ImageList cols={isMobile ? 1 : 2} gap={16}>
        {images.map((image, index) => (
          <ImageListItem
            key={index}
            sx={{
              cursor: 'pointer',
              borderRadius: 2,
              overflow: 'hidden',
              '&:hover': {
                opacity: 0.9,
              },
            }}
            onClick={() => setSelectedImage(image)}
          >
            <img
              src={image.url}
              alt={image.alt}
              loading="lazy"
              style={{
                width: '100%',
                height: 250,
                objectFit: 'cover',
              }}
              onError={(e) => {
                (e.target as HTMLImageElement).style.display = 'none';
              }}
            />
            <Box
              sx={{
                position: 'absolute',
                bottom: 0,
                left: 0,
                right: 0,
                bgcolor: 'rgba(0,0,0,0.7)',
                color: 'white',
                p: 1,
              }}
            >
              <Typography variant="caption" sx={{ display: 'block' }}>
                {image.caption}
              </Typography>
            </Box>
          </ImageListItem>
        ))}
      </ImageList>

      <Dialog
        open={!!selectedImage}
        onClose={() => setSelectedImage(null)}
        maxWidth="lg"
        fullWidth
      >
        <DialogContent sx={{ p: 0, position: 'relative' }}>
          <IconButton
            onClick={() => setSelectedImage(null)}
            sx={{
              position: 'absolute',
              top: 8,
              right: 8,
              bgcolor: 'rgba(0,0,0,0.5)',
              color: 'white',
              '&:hover': {
                bgcolor: 'rgba(0,0,0,0.7)',
              },
            }}
          >
            <Close />
          </IconButton>
          {selectedImage && (
            <Box>
              <img
                src={selectedImage.url}
                alt={selectedImage.alt}
                style={{
                  width: '100%',
                  maxHeight: '80vh',
                  objectFit: 'contain',
                }}
              />
              <Box sx={{ p: 2, bgcolor: 'background.paper' }}>
                <Typography variant="body2">{selectedImage.caption}</Typography>
              </Box>
            </Box>
          )}
        </DialogContent>
      </Dialog>
    </Box>
  );
}
