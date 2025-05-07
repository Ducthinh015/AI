from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .services import DraughtsGame

game = DraughtsGame()

@api_view(['GET'])
def init_board(request):
    # Giả sử game.init_board() trả về một bảng cờ dưới dạng danh sách 2D
    board = game.init_board()
    
    # Kiểm tra xem board có đúng cấu trúc chưa
    if board is None:
        return Response({"error": "Không thể khởi tạo bàn cờ."}, status=status.HTTP_400_BAD_REQUEST)
    
    return Response({'board': board})


@api_view(['GET'])
def get_moves(request):
    position = request.query_params.get('position')
    moves = game.get_valid_moves(position)
    return Response({'moves': moves})




@api_view(['POST'])
def make_move(request):
    from_pos = request.data.get('from') or request.data.get('from_pos')
    to_pos = request.data.get('to') or request.data.get('to_pos')

    if not from_pos or not to_pos:
        return Response(
            {"error": "Thiếu 'from' hoặc 'to' trong dữ liệu gửi."},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        result = game.make_move(from_pos, to_pos)
        if isinstance(result, dict) and result.get("error"):
            return Response(result, status=status.HTTP_400_BAD_REQUEST)
        return Response(result)
    except IndexError:
        return Response(
            {"error": "Vị trí nằm ngoài phạm vi bảng cờ."},
            status=status.HTTP_400_BAD_REQUEST
        )
    except Exception as e:
        return Response(
            {"error": f"Lỗi không xác định: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
