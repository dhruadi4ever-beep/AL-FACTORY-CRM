package com.aryanlace

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Card
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp

private data class ParcelUiModel(
    val id: Int,
    val parcelCode: String,
    val totalPcs: String,
    val items: String,
)

@Composable
fun PackingScreen() {
    val parcels = remember {
        listOf(
            ParcelUiModel(1, "PCL-001", "350", "Item A: 200 PCS, Item B: 150 PCS"),
            ParcelUiModel(2, "PCL-002", "300", "Item A: 300 PCS"),
        )
    }

    var parcelCode by remember { mutableStateOf("PCL-001") }
    var itemCode by remember { mutableStateOf("ITM-A") }
    var pcsQuantity by remember { mutableStateOf("200") }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp),
        verticalArrangement = Arrangement.spacedBy(12.dp)
    ) {
        Text(text = "Packing & Parcel Management", style = MaterialTheme.typography.headlineMedium)
        Text(text = "Group finished PCS into dispatch-ready parcels")

        Card(modifier = Modifier.fillMaxWidth(), shape = RoundedCornerShape(12.dp)) {
            Column(modifier = Modifier.padding(12.dp), verticalArrangement = Arrangement.spacedBy(8.dp)) {
                OutlinedTextField(value = parcelCode, onValueChange = { parcelCode = it }, label = { Text("Parcel code") }, modifier = Modifier.fillMaxWidth())
                OutlinedTextField(value = itemCode, onValueChange = { itemCode = it }, label = { Text("Item") }, modifier = Modifier.fillMaxWidth())
                OutlinedTextField(value = pcsQuantity, onValueChange = { pcsQuantity = it }, label = { Text("PCS quantity") }, modifier = Modifier.fillMaxWidth())
            }
        }

        Text(text = "Parcels", style = MaterialTheme.typography.titleMedium)
        LazyColumn(verticalArrangement = Arrangement.spacedBy(8.dp)) {
            items(parcels) { parcel ->
                Card(modifier = Modifier.fillMaxWidth(), shape = RoundedCornerShape(12.dp)) {
                    Column(modifier = Modifier.padding(12.dp), verticalArrangement = Arrangement.spacedBy(4.dp)) {
                        Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween, verticalAlignment = Alignment.CenterVertically) {
                            Text(text = parcel.parcelCode, style = MaterialTheme.typography.titleSmall)
                            Text(text = "${parcel.totalPcs} PCS")
                        }
                        Text(text = parcel.items)
                    }
                }
            }
        }
    }
}
