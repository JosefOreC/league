from simulacion.infrastructure.persistence.reto_analisis_repository import (
    obtener_retos_del_torneo, clasificar_criterio,
)


class ObtenerRetosUseCase:
    def ejecutar(self, torneo_id: str, caso_filtro: str = None) -> dict:
        filas = obtener_retos_del_torneo(torneo_id)
        if not filas:
            raise ValueError(f'No existe torneo con id={torneo_id}')

        resultado = {
            'torneo_id':        filas[0]['torneo_id'],
            'torneo_nombre':    filas[0]['torneo_nombre'],
            'reto_descripcion': filas[0]['reto_descripcion'],
            'categoria':        filas[0]['categoria'],
            'criterios':        [],
        }

        for fila in filas:
            caso = clasificar_criterio(
                fila['criterio_nombre'],
                fila['criterio_descripcion'],
            )
            if caso is None:
                continue
            if caso_filtro and caso != caso_filtro:
                continue
            resultado['criterios'].append({
                'criterio_id':             fila['criterio_id'],
                'criterio_nombre':         fila['criterio_nombre'],
                'criterio_descripcion':    fila['criterio_descripcion'],
                'caso':                    caso,
                'peso':                    float(fila['peso']),
                'min_value_qualification': fila['min_value_qualification'],
                'max_value_qualification': fila['max_value_qualification'],
                'validation_list':         fila['validation_list'],
            })

        return resultado
