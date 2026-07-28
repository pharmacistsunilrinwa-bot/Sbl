import pandas as pd
import numpy as np
from typing import Dict, Any, List
import json

class DataAnalysisService:
    @staticmethod
    def _convert_numpy_types(obj):
        """Convert numpy types to native Python types for JSON serialization"""
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, dict):
            return {key: DataAnalysisService._convert_numpy_types(value) for key, value in obj.items()}
        elif isinstance(obj, (list, tuple)):
            return [DataAnalysisService._convert_numpy_types(item) for item in obj]
        return obj

    @staticmethod
    def analyze_csv(file_path: str) -> Dict[str, Any]:
        try:
            df = pd.read_csv(file_path)
            
            # Calculate statistics with proper type conversion
            summary = {
                "columns": list(df.columns),
                "shape": list(df.shape),
                "rows": int(df.shape[0]),
                "columns_count": int(df.shape[1]),
                "describe": DataAnalysisService._convert_numpy_types(df.describe().to_dict()),
                "missing_values": DataAnalysisService._convert_numpy_types(df.isnull().sum().to_dict()),
                "data_types": {str(col): str(dtype) for col, dtype in df.dtypes.items()},
                "correlation": DataAnalysisService._convert_numpy_types(
                    df.select_dtypes(include=[np.number]).corr().to_dict()
                )
            }
            return {
                "success": True,
                "data": summary,
                "message": "CSV analysis completed successfully"
            }
        except FileNotFoundError:
            return {
                "success": False,
                "error": "File not found",
                "message": f"The file at {file_path} was not found"
            }
        except pd.errors.EmptyDataError:
            return {
                "success": False,
                "error": "Empty CSV",
                "message": "The CSV file is empty"
            }
        except Exception as e:
            return {
                "success": False,
                "error": type(e).__name__,
                "message": f"Error analyzing CSV: {str(e)}"
            }

    @staticmethod
    def calculate_statistics(data: List[float]) -> Dict[str, float]:
        try:
            arr = np.array(data)
            return {
                "mean": float(np.mean(arr)),
                "median": float(np.median(arr)),
                "std": float(np.std(arr)),
                "variance": float(np.var(arr)),
                "min": float(np.min(arr)),
                "max": float(np.max(arr)),
                "sum": float(np.sum(arr)),
                "count": int(len(arr))
            }
        except Exception as e:
            return {
                "error": f"Failed to calculate statistics: {str(e)}"
            }

analysis_service = DataAnalysisService()
