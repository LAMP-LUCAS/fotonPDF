from typing import Tuple, Dict

class GeometryService:
    """
    Serviço de domínio para manipulação de coordenadas e dimensões físicas.
    Converte entre PDF Points (1/72 pol) e unidades métricas (Milímetros).
    """

    POINTS_TO_MM = 25.4 / 72.0

    @staticmethod
    def points_to_mm(points: float) -> float:
        """Converte pontos do PDF para milímetros."""
        return round(points * GeometryService.POINTS_TO_MM, 2)

    @staticmethod
    def mm_to_points(mm: float) -> float:
        """Converte milímetros para pontos do PDF."""
        return mm / GeometryService.POINTS_TO_MM

    @classmethod
    def get_rect_dimensions_mm(cls, rect: Tuple[float, float, float, float]) -> Dict[str, float]:
        """
        Calcula dimensões e centro de um retângulo em mm.
        Entrada: (x0, y0, x1, y1) em pontos.
        """
        x0, y0, x1, y1 = rect
        width_pts = abs(x1 - x0)
        height_pts = abs(y1 - y0)
        
        width_mm = cls.points_to_mm(width_pts)
        height_mm = cls.points_to_mm(height_pts)
        
        # Centro da seleção
        cx_mm = cls.points_to_mm(x0 + width_pts / 2)
        cy_mm = cls.points_to_mm(y0 + height_pts / 2)
        
        return {
            "width_mm": width_mm,
            "height_mm": height_mm,
            "center_x_mm": cx_mm,
            "center_y_mm": cy_mm,
            "area_mm2": round(width_mm * height_mm, 2)
        }

    @staticmethod
    def identify_aec_format(width_pts: float, height_pts: float) -> str:
        """
        Identifica o formato da folha (A0-A4) com base nas dimensões em pontos.
        Aceita margem de erro de 5mm para considerar variações de crop/bleed.
        """
        w_mm = GeometryService.points_to_mm(max(width_pts, height_pts))
        h_mm = GeometryService.points_to_mm(min(width_pts, height_pts))

        # Tabela de formatos ABNT/ISO (Longo x Curto) em mm
        formats = {
            "A0": (1189, 841),
            "A1": (841, 594),
            "A2": (594, 420),
            "A3": (420, 297),
            "A4": (297, 210),
        }

        tolerance = 10.0 # 10mm de tolerância para formatos AEC

        for name, (fw, fh) in formats.items():
            if abs(w_mm - fw) < tolerance and abs(h_mm - fh) < tolerance:
                return name
        
        return f"Custom ({int(w_mm)}x{int(h_mm)}mm)"
