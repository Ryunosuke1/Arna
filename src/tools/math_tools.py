from typing import Union, List
from sympy import (
    sympify, solve, integrate, diff,
    Symbol, Expr, SympifyError
)
import logging

class MathTools:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    async def evaluate(self, expression: str) -> Union[float, str]:
        """
        数式を評価する
        
        Args:
            expression: 評価する数式（例: "2 * sin(pi/4) + 3"）
        
        Returns:
            計算結果、またはエラーメッセージ
        """
        try:
            # 文字列を数式に変換
            expr = sympify(expression)
            # 数値計算を実行
            result = float(expr.evalf())
            return result
        except SympifyError as e:
            error_msg = f"Invalid expression format: {str(e)}"
            self.logger.error(error_msg)
            return error_msg
        except Exception as e:
            error_msg = f"Error evaluating expression: {str(e)}"
            self.logger.error(error_msg)
            return error_msg
    
    async def solve_equation(self, equation: str) -> Union[List[str], str]:
        """
        方程式を解く
        
        Args:
            equation: 解く方程式（例: "x**2 - 4 = 0"）
        
        Returns:
            解のリスト、またはエラーメッセージ
        """
        try:
            # '=' の両辺を分離
            if '=' in equation:
                left, right = equation.split('=')
                # 方程式を標準形に変形（全て左辺に移項）
                equation = f"({left}) - ({right})"
            
            # 方程式を解く
            x = Symbol('x')
            expr = sympify(equation)
            solutions = solve(expr, x)
            
            # 解を文字列のリストに変換
            return [str(sol) for sol in solutions]
        except SympifyError as e:
            error_msg = f"Invalid equation format: {str(e)}"
            self.logger.error(error_msg)
            return error_msg
        except Exception as e:
            error_msg = f"Error solving equation: {str(e)}"
            self.logger.error(error_msg)
            return error_msg
    
    async def integrate(self, expression: str) -> Union[str, Expr]:
        """
        式を積分する
        
        Args:
            expression: 積分する式（例: "x**2"）
        
        Returns:
            積分結果、またはエラーメッセージ
        """
        try:
            x = Symbol('x')
            expr = sympify(expression)
            result = integrate(expr, x)
            return str(result)
        except SympifyError as e:
            error_msg = f"Invalid expression format: {str(e)}"
            self.logger.error(error_msg)
            return error_msg
        except Exception as e:
            error_msg = f"Error integrating expression: {str(e)}"
            self.logger.error(error_msg)
            return error_msg
    
    async def differentiate(self, expression: str) -> Union[str, Expr]:
        """
        式を微分する
        
        Args:
            expression: 微分する式（例: "x**3"）
        
        Returns:
            微分結果、またはエラーメッセージ
        """
        try:
            x = Symbol('x')
            expr = sympify(expression)
            result = diff(expr, x)
            return str(result)
        except SympifyError as e:
            error_msg = f"Invalid expression format: {str(e)}"
            self.logger.error(error_msg)
            return error_msg
        except Exception as e:
            error_msg = f"Error differentiating expression: {str(e)}"
            self.logger.error(error_msg)
            return error_msg

    def _format_expression(self, expr: Union[str, Expr]) -> str:
        """数式を見やすい形式にフォーマット"""
        try:
            if isinstance(expr, str):
                expr = sympify(expr)
            return str(expr)
        except:
            return str(expr)
