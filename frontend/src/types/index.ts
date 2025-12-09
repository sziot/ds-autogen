export interface ReviewResult {
  success: boolean;
  architect_report?: string;
  reviewer_report?: string;
  optimizer_report?: string;
  fixed_code?: string;
  save_result?: {
    success: boolean;
    saved_path?: string;
    message?: string;
  };
  file_name?: string;
  message?: string;
}

export interface CodeFile {
  name: string;
  content: string;
}

