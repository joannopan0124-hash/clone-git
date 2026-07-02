import React, { useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload, File, Image, FileText, X } from 'lucide-react';
import { cn } from '@/lib/utils';

interface FileUploadProps {
  onFileUpload: (file: File) => void;
  uploadedFile: File | null;
  onClearFile: () => void;
  isUploading: boolean;
}

export default function FileUpload({
  onFileUpload,
  uploadedFile,
  onClearFile,
  isUploading,
}: FileUploadProps) {
  const onDrop = useCallback((acceptedFiles: File[]) => {
    if (acceptedFiles.length > 0) {
      onFileUpload(acceptedFiles[0]);
    }
  }, [onFileUpload]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'image/png': ['.png'],
      'image/jpeg': ['.jpg', '.jpeg'],
      'application/pdf': ['.pdf'],
    },
    maxSize: 10 * 1024 * 1024, // 10MB
    multiple: false,
  });

  const getFileIcon = (file: File) => {
    if (file.type.startsWith('image/')) {
      return <Image className="w-12 h-12 text-blue-500" />;
    } else if (file.type === 'application/pdf') {
      return <FileText className="w-12 h-12 text-red-500" />;
    }
    return <File className="w-12 h-12 text-gray-500" />;
  };

  return (
    <div className="w-full">
      {!uploadedFile ? (
        <div
          {...getRootProps()}
          className={cn(
            'border-2 border-dashed rounded-lg p-12 cursor-pointer transition-all duration-300',
            'hover:border-blue-500 hover:bg-blue-50',
            isDragActive
              ? 'border-blue-500 bg-blue-50 scale-105'
              : 'border-gray-300 bg-white'
          )}
        >
          <input {...getInputProps()} />
          <div className="flex flex-col items-center justify-center text-center">
            <Upload
              className={cn(
                'w-16 h-16 mb-4 transition-all duration-300',
                isDragActive ? 'text-blue-500 animate-bounce' : 'text-gray-400'
              )}
            />
            <p className="text-lg font-medium text-gray-700 mb-2">
              {isDragActive ? '拖放文件到此处' : '拖放文件或点击上传'}
            </p>
            <p className="text-sm text-gray-500 mb-4">
              支持 PNG、JPG、JPEG、PDF 格式，最大 10MB
            </p>
            <div className="flex gap-2">
              <span className="px-3 py-1 bg-blue-100 text-blue-700 rounded-full text-xs">
                图片
              </span>
              <span className="px-3 py-1 bg-red-100 text-red-700 rounded-full text-xs">
                PDF
              </span>
            </div>
          </div>
        </div>
      ) : (
        <div className="bg-white border rounded-lg p-6 shadow-md">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              {getFileIcon(uploadedFile)}
              <div>
                <p className="font-medium text-gray-800">{uploadedFile.name}</p>
                <p className="text-sm text-gray-500">
                  {(uploadedFile.size / 1024 / 1024).toFixed(2)} MB
                </p>
              </div>
            </div>
            <button
              onClick={onClearFile}
              className="p-2 hover:bg-gray-100 rounded-full transition-colors"
              disabled={isUploading}
            >
              <X className="w-5 h-5 text-gray-500" />
            </button>
          </div>
          {isUploading && (
            <div className="mt-4">
              <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
                <div className="h-full bg-blue-500 animate-pulse rounded-full" />
              </div>
              <p className="text-sm text-gray-500 mt-2 text-center">上传中...</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}